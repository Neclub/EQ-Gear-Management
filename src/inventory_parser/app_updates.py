"""Check GitHub Releases for a newer EQGM executable."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from inventory_parser import __version__

GITHUB_OWNER = "Neclub"
GITHUB_REPO = "EQ-Gear-Management"
GITHUB_API_LATEST = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)
DOWNLOAD_URL_PREFIX = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/"
USER_AGENT = "EQGM (update check; local tool)"
_TIMEOUT_SECONDS = 10
_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_EXE_NAME_RE = re.compile(r"^EQGM-.+\.exe$", re.IGNORECASE)


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


def exe_asset_url(payload: dict) -> str | None:
    for asset in payload.get("assets") or []:
        name = str(asset.get("name") or "")
        url = str(asset.get("browser_download_url") or "").strip()
        if _EXE_NAME_RE.fullmatch(name) and url.startswith(DOWNLOAD_URL_PREFIX):
            return url
    return None


def is_allowed_download_url(url: str) -> bool:
    return bool(url) and url.startswith(DOWNLOAD_URL_PREFIX) and url.endswith(".exe")


def _fetch_latest_payload(timeout: float = _TIMEOUT_SECONDS) -> dict:
    req = urllib.request.Request(
        GITHUB_API_LATEST,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("Unexpected GitHub response.")
    return data


def check_for_updates(current: str | None = None) -> dict:
    running = current if current is not None else __version__
    try:
        payload = _fetch_latest_payload()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "status": "error",
            "current": running,
            "latest": None,
            "downloadUrl": None,
            "message": str(exc) or "Could not reach GitHub Releases.",
        }

    latest = normalize_tag(str(payload.get("tag_name") or ""))
    if parse_version(latest) is None:
        return {
            "ok": False,
            "status": "error",
            "current": running,
            "latest": latest or None,
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
            "message": "Latest GitHub release has no EQGM .exe asset.",
        }

    return {
        "ok": True,
        "status": "update",
        "current": running,
        "latest": latest,
        "downloadUrl": download_url,
        "message": f"Version {latest} is available.",
    }
