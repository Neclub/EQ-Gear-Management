"""Seed %LOCALAPPDATA%\\EQGM\\ caches from the EQGM-Web GitHub prebuilt cache."""

from __future__ import annotations

import io
import hashlib
import json
import re
import tempfile
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from inventory_parser.generate_log import record_cache, record_problem
from inventory_parser.raid_bis.catalog import ITEM_CACHE_VERSION
from inventory_parser.raid_bis.icons import resolve_icon_png_path
from inventory_parser.slot2_augs.paths import (
    CACHE_FILENAMES,
    ICON_CACHE_DIRNAME,
    appdata_dir,
)

GITHUB_OWNER = "Neclub"
GITHUB_REPO = "EQGM-Web"
GITHUB_API_HOST = "api.github.com"
GITHUB_DOWNLOAD_HOST = "github.com"
CODELOAD_HOST = "codeload.github.com"
USER_AGENT = "EQGM (prebuilt cache; local tool)"

CACHE_CONTENTS_URL = (
    f"https://{GITHUB_API_HOST}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/cache?ref=main"
)
ZIPBALL_URL = (
    f"https://{CODELOAD_HOST}/{GITHUB_OWNER}/{GITHUB_REPO}/zip/refs/heads/main"
)

META_FILENAME = "prebuilt_cache_meta.json"
_TIMEOUT_SECONDS = 15
_DOWNLOAD_TIMEOUT_SECONDS = 180
_MAX_API_BYTES = 1_048_576
_MAX_ZIP_BYTES = 150 * 1024 * 1024
_MAX_URL_LENGTH = 500

_ALLOWED_ZIP_REDIRECT_HOSTS = frozenset(
    {
        CODELOAD_HOST,
        GITHUB_DOWNLOAD_HOST,
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)

# Item-id keyed maps: union keys; local entry wins on conflict.
_MAP_FILENAMES = frozenset(
    {
        "eqresource_aug_cache.json",
        "eqresource_expansion_cache.json",
        "eqresource_gear_tier_cache.json",
        "eqresource_type18_item_meta_cache.json",
        "item_sockets_cache.json",
        "item_class_cache.json",
        "raid_bis_item_cache.json",
    }
)
# Whole-catalog / profile snapshots: prefer newer fetched_at, else keep local.
_CATALOG_FILENAMES = frozenset(
    {
        "raid_bis_catalog.json",
        "eqresource_search_cache.json",
        "eqresource_type18_catalog_cache.json",
        "raidloot_cache.json",
    }
)
_PROFILE_CATALOG_FILENAMES = frozenset(
    {
        "eqresource_search_cache.json",
        "raidloot_cache.json",
    }
)

_ICON_NAME_RE = re.compile(r"^(\d+)\.png$")
_EXPAC_NAME_RE = re.compile(r"^expac-[a-z0-9_-]+\.(jpg|png)$", re.IGNORECASE)
_SHARD_RE = re.compile(r"^\d+$")

StatusFn = Callable[[str], None]


@dataclass
class SeedResult:
    """Outcome of one prebuilt-cache seed attempt."""

    ok: bool
    skipped: bool = False
    reason: str = ""
    sha: str | None = None
    files_written: list[str] = field(default_factory=list)
    icons_copied: int = 0
    error: str | None = None


class _SameHostHttpsRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow HTTPS redirects only while the host stays on the GitHub API."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != GITHUB_API_HOST:
            raise urllib.error.URLError("Refusing redirect away from GitHub API.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _ZipDownloadRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow HTTPS redirects only to GitHub download / codeload hosts."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or host not in _ALLOWED_ZIP_REDIRECT_HOSTS:
            raise urllib.error.URLError(
                f"Refusing zip download redirect to {parsed.hostname!r}."
            )
        if parsed.username or parsed.password:
            raise urllib.error.URLError("Refusing zip download redirect with credentials.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def meta_path() -> Path:
    return appdata_dir() / META_FILENAME


def _load_meta() -> dict:
    path = meta_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_meta(sha: str) -> None:
    payload = {
        "sha": sha,
        "repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "pulled_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    meta_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")


def delete_prebuilt_meta() -> bool:
    """Remove the prebuilt-cache meta file so the next generate re-seeds."""
    path = meta_path()
    if not path.exists():
        return False
    try:
        path.unlink()
        return True
    except OSError:
        return False


def fetch_cache_tree_sha(timeout: float = _TIMEOUT_SECONDS) -> str:
    """Return the GitHub tree SHA (or a stable fingerprint) for ``cache/``."""
    # Prefer the object form so we get the real tree SHA when GitHub supports it.
    req = urllib.request.Request(
        CACHE_CONTENTS_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github.object+json",
        },
    )
    opener = urllib.request.build_opener(_SameHostHttpsRedirectHandler)
    with opener.open(req, timeout=timeout) as resp:
        final = urlparse(resp.geturl())
        if final.scheme != "https" or final.hostname != GITHUB_API_HOST:
            raise ValueError("Unexpected GitHub response host.")
        body = resp.read(_MAX_API_BYTES + 1)
    if len(body) > _MAX_API_BYTES:
        raise ValueError("GitHub response too large.")
    data = json.loads(body.decode("utf-8"))
    if isinstance(data, dict) and data.get("sha"):
        return str(data["sha"])
    if isinstance(data, list):
        parts: list[str] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name") or "")
            sha = str(entry.get("sha") or "")
            if name and sha:
                parts.append(f"{name}:{sha}")
        if not parts:
            raise ValueError("Empty GitHub cache listing.")
        return hashlib.sha1("\n".join(sorted(parts)).encode("utf-8")).hexdigest()
    raise ValueError("Unexpected GitHub cache listing.")


def _download_zipball() -> bytes:
    if not isinstance(ZIPBALL_URL, str) or len(ZIPBALL_URL) > _MAX_URL_LENGTH:
        raise ValueError("Unexpected zip URL.")
    req = urllib.request.Request(
        ZIPBALL_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/zip",
        },
    )
    opener = urllib.request.build_opener(_ZipDownloadRedirectHandler)
    with opener.open(req, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as resp:
        final = urlparse(resp.geturl())
        host = (final.hostname or "").lower()
        if final.scheme != "https" or host not in _ALLOWED_ZIP_REDIRECT_HOSTS:
            raise ValueError("Unexpected zip download host.")
        length_hdr = resp.headers.get("Content-Length")
        if length_hdr is not None:
            try:
                if int(length_hdr) > _MAX_ZIP_BYTES:
                    raise ValueError("Prebuilt cache zip is too large.")
            except ValueError as exc:
                if "too large" in str(exc):
                    raise
        buf = io.BytesIO()
        written = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            written += len(chunk)
            if written > _MAX_ZIP_BYTES:
                raise ValueError("Prebuilt cache zip is too large.")
            buf.write(chunk)
    data = buf.getvalue()
    if len(data) < 4 or data[:2] != b"PK":
        raise ValueError("Downloaded file is not a zip archive.")
    return data


def _cache_relative_path(member_name: str) -> str | None:
    """Return path under cache/ for a zip member, or None if not allowed."""
    # Zip members look like EQGM-Web-main/cache/...
    parts = member_name.replace("\\", "/").split("/")
    try:
        idx = parts.index("cache")
    except ValueError:
        return None
    rel_parts = parts[idx + 1 :]
    if not rel_parts or any(p in ("", ".", "..") for p in rel_parts):
        return None
    return "/".join(rel_parts)


def _is_allowed_cache_member(rel: str) -> bool:
    parts = rel.split("/")
    if len(parts) == 1:
        return parts[0] in CACHE_FILENAMES
    if parts[0] != ICON_CACHE_DIRNAME:
        return False
    if len(parts) == 2:
        # item_icons/expac-foo.jpg or (legacy) item_icons/123.png
        name = parts[1]
        if _EXPAC_NAME_RE.fullmatch(name):
            return True
        return bool(_ICON_NAME_RE.fullmatch(name))
    if len(parts) == 3:
        # item_icons/{shard}/{id}.png
        shard, name = parts[1], parts[2]
        if not _SHARD_RE.fullmatch(shard):
            return False
        match = _ICON_NAME_RE.fullmatch(name)
        if not match:
            return False
        # Shard must match id // 1000
        icon_id = int(match.group(1))
        return str(icon_id // 1000) == shard
    return False


def _parse_fetched_at(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _load_json_bytes(raw: bytes) -> dict | None:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _load_local_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def merge_map_cache(local: dict, remote: dict, *, require_item_version: bool = False) -> dict:
    """Union item-id maps; local entries win on conflict."""
    if require_item_version:
        remote_ver = int(remote.get("_version") or 0)
        if remote_ver != ITEM_CACHE_VERSION:
            return dict(local) if local else {}
    out = {k: v for k, v in remote.items() if k != "_version"}
    for key, value in local.items():
        if key == "_version":
            continue
        out[key] = value
    if require_item_version or "_version" in local or "_version" in remote:
        out["_version"] = int(local.get("_version") or remote.get("_version") or ITEM_CACHE_VERSION)
    return out


def merge_catalog_file(local: dict, remote: dict, *, profile_keyed: bool) -> dict:
    """Merge catalog snapshots; keep newer fetched_at, else prefer local."""
    if not local:
        return dict(remote)
    if not remote:
        return dict(local)
    if profile_keyed:
        out = dict(remote)
        for key, local_entry in local.items():
            remote_entry = out.get(key)
            if not isinstance(local_entry, dict):
                out[key] = local_entry
                continue
            if not isinstance(remote_entry, dict):
                out[key] = local_entry
                continue
            local_ts = _parse_fetched_at(local_entry.get("fetched_at"))
            remote_ts = _parse_fetched_at(remote_entry.get("fetched_at"))
            if remote_ts is None or (local_ts is not None and local_ts >= remote_ts):
                out[key] = local_entry
        return out
    local_ts = _parse_fetched_at(local.get("fetched_at"))
    # raid_bis_catalog nests fetched_at under catalog
    if local_ts is None and isinstance(local.get("catalog"), dict):
        local_ts = _parse_fetched_at(local["catalog"].get("fetched_at"))
    remote_ts = _parse_fetched_at(remote.get("fetched_at"))
    if remote_ts is None and isinstance(remote.get("catalog"), dict):
        remote_ts = _parse_fetched_at(remote["catalog"].get("fetched_at"))
    if remote_ts is None or (local_ts is not None and local_ts >= remote_ts):
        return dict(local)
    return dict(remote)


def _merge_json_file(name: str, local_path: Path, remote_bytes: bytes) -> bool:
    """Merge remote JSON into local_path. Returns True if the file was written."""
    remote = _load_json_bytes(remote_bytes)
    if remote is None:
        return False
    local = _load_local_json(local_path)
    if name in _MAP_FILENAMES:
        merged = merge_map_cache(
            local,
            remote,
            require_item_version=(name == "raid_bis_item_cache.json"),
        )
        if not merged:
            return False
        if merged == local and local_path.is_file():
            return False
        _write_json(local_path, merged)
        return True
    if name in _CATALOG_FILENAMES:
        merged = merge_catalog_file(
            local,
            remote,
            profile_keyed=name in _PROFILE_CATALOG_FILENAMES,
        )
        if not merged:
            return False
        if merged == local and local_path.is_file():
            return False
        _write_json(local_path, merged)
        return True
    # Unknown but allowlisted name: copy only if missing.
    if local_path.is_file():
        return False
    _write_json(local_path, remote)
    return True


def _copy_icon_member(rel: str, data: bytes, dest_root: Path) -> bool:
    """Copy an icon/expac file if the desktop resolver would miss it."""
    parts = rel.split("/")
    if parts[0] != ICON_CACHE_DIRNAME:
        return False
    icons_root = dest_root / ICON_CACHE_DIRNAME
    if len(parts) == 2:
        name = parts[1]
        if _EXPAC_NAME_RE.fullmatch(name):
            dest = icons_root / name
            if dest.is_file():
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return True
        match = _ICON_NAME_RE.fullmatch(name)
        if not match:
            return False
        icon_id = match.group(1)
        if resolve_icon_png_path(icon_id, cache_dir=icons_root) is not None:
            return False
        dest = icons_root / f"{icon_id}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    if len(parts) == 3:
        shard, name = parts[1], parts[2]
        match = _ICON_NAME_RE.fullmatch(name)
        if not match:
            return False
        icon_id = match.group(1)
        if resolve_icon_png_path(icon_id, cache_dir=icons_root) is not None:
            return False
        dest = icons_root / shard / f"{icon_id}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    return False


def apply_zip_to_appdata(zip_bytes: bytes, *, dest_root: Path | None = None) -> SeedResult:
    """Extract and merge allowlisted cache members from a zipball into AppData."""
    root = dest_root if dest_root is not None else appdata_dir()
    root.mkdir(parents=True, exist_ok=True)
    files_written: list[str] = []
    icons_copied = 0
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        return SeedResult(ok=False, error=f"Invalid zip: {exc}")

    with zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel = _cache_relative_path(info.filename)
            if rel is None or not _is_allowed_cache_member(rel):
                continue
            # Zip-slip: reject absolute / escaped paths after normalize.
            dest_check = (root / rel).resolve()
            try:
                dest_check.relative_to(root.resolve())
            except ValueError:
                continue
            try:
                data = zf.read(info)
            except (OSError, zipfile.BadZipFile, RuntimeError):
                continue
            if rel.startswith(f"{ICON_CACHE_DIRNAME}/"):
                if _copy_icon_member(rel, data, root):
                    icons_copied += 1
                continue
            name = Path(rel).name
            if name not in CACHE_FILENAMES:
                continue
            local_path = root / name
            if _merge_json_file(name, local_path, data):
                files_written.append(name)

    return SeedResult(
        ok=True,
        files_written=files_written,
        icons_copied=icons_copied,
    )


def seed_prebuilt_cache(
    *,
    on_status: StatusFn | None = None,
    force: bool = False,
    dest_root: Path | None = None,
    fetch_sha: Callable[[], str] | None = None,
    download_zip: Callable[[], bytes] | None = None,
) -> SeedResult:
    """
    Pull the EQGM-Web ``cache/`` tree into AppData when missing or outdated.

    Fail-open: network or parse errors return ``ok=False`` without raising so
    Generate Report can continue with live fetches.
    """
    root = dest_root if dest_root is not None else appdata_dir()

    def _status(message: str) -> None:
        if on_status is not None:
            on_status(message)

    try:
        sha_fn = fetch_sha or fetch_cache_tree_sha
        sha = sha_fn()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
        record_problem(f"Prebuilt cache: could not check GitHub ({exc})")
        return SeedResult(ok=False, skipped=True, reason="sha_check_failed", error=str(exc))

    meta = _load_meta() if dest_root is None else {}
    if dest_root is not None:
        meta_file = root / META_FILENAME
        if meta_file.is_file():
            try:
                loaded = json.loads(meta_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    meta = loaded
            except (OSError, json.JSONDecodeError):
                meta = {}

    local_present = any((root / name).is_file() for name in CACHE_FILENAMES) or (
        (root / ICON_CACHE_DIRNAME).is_dir()
        and any((root / ICON_CACHE_DIRNAME).rglob("*.png"))
    )
    if (
        not force
        and meta.get("sha") == sha
        and local_present
    ):
        return SeedResult(ok=True, skipped=True, reason="up_to_date", sha=sha)

    _status("Downloading catalog cache from GitHub…")
    try:
        zip_fn = download_zip or _download_zipball
        zip_bytes = zip_fn()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        record_problem(f"Prebuilt cache: download failed ({exc})")
        return SeedResult(ok=False, skipped=True, reason="download_failed", sha=sha, error=str(exc))

    # Optionally stage to a temp file under AppData for crash safety.
    staging_dir = root / "updates"
    try:
        staging_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix="eqgm-web-cache-",
            suffix=".zip",
            dir=str(staging_dir),
            delete=False,
        ) as tmp:
            tmp.write(zip_bytes)
            tmp_path = Path(tmp.name)
    except OSError:
        tmp_path = None

    try:
        result = apply_zip_to_appdata(zip_bytes, dest_root=root)
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    if not result.ok:
        return result

    result.sha = sha
    try:
        if dest_root is None:
            _save_meta(sha)
        else:
            (root / META_FILENAME).write_text(
                json.dumps(
                    {
                        "sha": sha,
                        "repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
                        "pulled_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
    except OSError as exc:
        record_problem(f"Prebuilt cache: could not save meta ({exc})")

    detail_parts: list[str] = []
    if result.files_written:
        detail_parts.append(f"{len(result.files_written)} json")
    if result.icons_copied:
        detail_parts.append(f"{result.icons_copied} icons")
    detail = ", ".join(detail_parts) if detail_parts else "no changes"
    record_cache("Prebuilt GitHub cache", detail)
    return result
