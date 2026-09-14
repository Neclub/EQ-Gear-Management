"""Check GitHub Releases and download/launch a newer EQGM installer."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

from inventory_parser import __version__
from inventory_parser.slot2_augs.paths import appdata_dir

GITHUB_OWNER = "Neclub"
GITHUB_REPO = "EQ-Gear-Management"
GITHUB_API_HOST = "api.github.com"
GITHUB_DOWNLOAD_HOST = "github.com"
GITHUB_API_LATEST = (
    f"https://{GITHUB_API_HOST}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)
DOWNLOAD_URL_PREFIX = f"https://{GITHUB_DOWNLOAD_HOST}/{GITHUB_OWNER}/{GITHUB_REPO}/"
USER_AGENT = "EQGM (update check; local tool)"
_TIMEOUT_SECONDS = 10
_DOWNLOAD_TIMEOUT_SECONDS = 120
_MAX_BODY_BYTES = 1_048_576
_MAX_INSTALLER_BYTES = 200 * 1024 * 1024
_MAX_URL_LENGTH = 500
_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_EXE_NAME_RE = re.compile(r"^EQGM-install-\d+\.\d+\.\d+\.exe$")
_DOWNLOAD_PATH_RE = re.compile(
    rf"^/{re.escape(GITHUB_OWNER)}/{re.escape(GITHUB_REPO)}"
    r"/releases/download/(v?(\d+\.\d+\.\d+))/EQGM-install-(\d+\.\d+\.\d+)\.exe$"
)
_ALLOWED_DOWNLOAD_REDIRECT_HOSTS = frozenset(
    {
        GITHUB_DOWNLOAD_HOST,
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com",
    }
)


class _SameHostHttpsRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow HTTPS redirects only while the host stays on the GitHub API."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != GITHUB_API_HOST:
            raise urllib.error.URLError("Refusing redirect away from GitHub API.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _InstallerDownloadRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow HTTPS redirects only to GitHub download / release CDN hosts."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or host not in _ALLOWED_DOWNLOAD_REDIRECT_HOSTS:
            raise urllib.error.URLError(
                f"Refusing installer download redirect to {parsed.hostname!r}."
            )
        if parsed.username or parsed.password:
            raise urllib.error.URLError("Refusing installer download redirect with credentials.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def parse_version(value: str) -> tuple[int, int, int] | None:
    text = (value or "").strip()
    match = _VERSION_RE.fullmatch(text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def normalize_tag(tag_name: str) -> str:
    text = (tag_name or "").strip()
    if text.startswith("v") or text.startswith("V"):
        return text[1:]
    return text


def is_newer(latest: str, current: str) -> bool:
    latest_parts = parse_version(latest)
    current_parts = parse_version(current)
    if latest_parts is None or current_parts is None:
        return False
    return latest_parts > current_parts


def is_allowed_download_url(url: str) -> bool:
    """True only for this repo's HTTPS GitHub Release EQGM-install-x.y.z.exe asset."""
    if not isinstance(url, str) or not url or len(url) > _MAX_URL_LENGTH:
        return False
    if any(ord(ch) < 32 or ch == "\\" for ch in url):
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    if parsed.username or parsed.password:
        return False
    if parsed.hostname != GITHUB_DOWNLOAD_HOST:
        return False
    if parsed.port not in (None, 443):
        return False
    if parsed.query or parsed.params or parsed.fragment:
        return False
    match = _DOWNLOAD_PATH_RE.fullmatch(unquote(parsed.path))
    if not match:
        return False
    return match.group(2) == match.group(3)


def installer_filename_from_url(url: str) -> str | None:
    if not is_allowed_download_url(url):
        return None
    name = Path(unquote(urlparse(url).path)).name
    if not _EXE_NAME_RE.fullmatch(name):
        return None
    return name


def exe_asset_url(payload: dict) -> str | None:
    for asset in payload.get("assets") or []:
        name = str(asset.get("name") or "")
        url = str(asset.get("browser_download_url") or "").strip()
        if _EXE_NAME_RE.fullmatch(name) and is_allowed_download_url(url):
            return url
    return None


def updates_dir() -> Path:
    path = appdata_dir() / "updates"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fetch_latest_payload(timeout: float = _TIMEOUT_SECONDS) -> dict:
    req = urllib.request.Request(
        GITHUB_API_LATEST,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    opener = urllib.request.build_opener(_SameHostHttpsRedirectHandler)
    with opener.open(req, timeout=timeout) as resp:
        final = urlparse(resp.geturl())
        if final.scheme != "https" or final.hostname != GITHUB_API_HOST:
            raise ValueError("Unexpected GitHub response host.")
        body = resp.read(_MAX_BODY_BYTES + 1)
    if len(body) > _MAX_BODY_BYTES:
        raise ValueError("GitHub response too large.")
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Unexpected GitHub response.")
    return data


def check_for_updates(current: str | None = None) -> dict:
    running = current if current is not None else __version__
    try:
        payload = _fetch_latest_payload()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError):
        return {
            "ok": False,
            "status": "error",
            "current": running,
            "latest": None,
            "downloadUrl": None,
            "message": "Could not reach GitHub Releases.",
        }

    latest = normalize_tag(str(payload.get("tag_name") or ""))
    if parse_version(latest) is None:
        return {
            "ok": False,
            "status": "error",
            "current": running,
            "latest": None,
            "downloadUrl": None,
            "message": "Latest GitHub release has an unexpected version tag.",
        }

    if not is_newer(latest, running):
        return {
            "ok": True,
            "status": "latest",
            "current": running,
            "latest": latest,
            "downloadUrl": None,
            "message": "You have the latest version.",
        }

    download_url = exe_asset_url(payload)
    if not download_url:
        return {
            "ok": False,
            "status": "error",
            "current": running,
            "latest": latest,
            "downloadUrl": None,
            "message": "Latest GitHub release has no EQGM installer asset.",
        }

    return {
        "ok": True,
        "status": "update",
        "current": running,
        "latest": latest,
        "downloadUrl": download_url,
        "message": (
            f"Newest version {latest} is available. "
            f"Current version is {running}."
        ),
    }


def _launch_installer(path: Path) -> None:
    if os.name == "nt":
        os.startfile(str(path))  # noqa: S606 — intentional: launch signed Inno setup
    else:
        subprocess.Popen([str(path)], shell=False, cwd=str(path.parent))  # noqa: S603


def download_and_launch_installer(url: str) -> dict:
    """Download an allowlisted installer to AppData and launch it."""
    filename = installer_filename_from_url(url)
    if not filename:
        return {"ok": False, "error": "Unexpected download URL."}

    dest = updates_dir() / filename
    partial = dest.with_suffix(dest.suffix + ".partial")
    if partial.exists():
        try:
            partial.unlink()
        except OSError:
            pass

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/octet-stream",
        },
    )
    opener = urllib.request.build_opener(_InstallerDownloadRedirectHandler)
    try:
        with opener.open(req, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as resp:
            final = urlparse(resp.geturl())
            host = (final.hostname or "").lower()
            if final.scheme != "https" or host not in _ALLOWED_DOWNLOAD_REDIRECT_HOSTS:
                return {"ok": False, "error": "Unexpected download host."}
            length_hdr = resp.headers.get("Content-Length")
            if length_hdr is not None:
                try:
                    if int(length_hdr) > _MAX_INSTALLER_BYTES:
                        return {"ok": False, "error": "Installer download is too large."}
                except ValueError:
                    pass

            first = resp.read(2)
            if first != b"MZ":
                return {"ok": False, "error": "Downloaded file is not a Windows installer."}

            written = len(first)
            with partial.open("wb") as out:
                out.write(first)
                while True:
                    chunk = resp.read(1024 * 256)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > _MAX_INSTALLER_BYTES:
                        out.close()
                        try:
                            partial.unlink()
                        except OSError:
                            pass
                        return {"ok": False, "error": "Installer download is too large."}
                    out.write(chunk)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        try:
            if partial.exists():
                partial.unlink()
        except OSError:
            pass
        return {"ok": False, "error": f"Could not download the installer. ({exc})"}

    try:
        if dest.exists():
            dest.unlink()
        partial.replace(dest)
    except OSError as exc:
        try:
            if partial.exists():
                partial.unlink()
        except OSError:
            pass
        return {"ok": False, "error": f"Could not save the installer. ({exc})"}

    try:
        _launch_installer(dest)
    except OSError as exc:
        return {"ok": False, "error": f"Could not start the installer. ({exc})"}

    return {"ok": True, "path": str(dest)}
