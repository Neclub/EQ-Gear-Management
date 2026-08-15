import json
from unittest.mock import patch

from inventory_parser.app_updates import (
    DOWNLOAD_URL_PREFIX,
    check_for_updates,
    exe_asset_url,
    is_allowed_download_url,
    is_newer,
    normalize_tag,
    parse_version,
)
from inventory_parser.web_api import WebApi


def _release_payload(tag: str, exe_name: str | None = None) -> dict:
    version = tag[1:] if tag.startswith("v") else tag
    name = exe_name if exe_name is not None else f"EQGM-{version}.exe"
    url = f"{DOWNLOAD_URL_PREFIX}releases/download/{tag}/{name}"
    return {
        "tag_name": tag,
        "assets": [{"name": name, "browser_download_url": url}],
    }


def test_parse_version_and_v_prefix() -> None:
    assert parse_version("1.21.0") == (1, 21, 0)
    assert parse_version("v1.22.0") == (1, 22, 0)
    assert parse_version("nope") is None
    assert normalize_tag("v1.21.0") == "1.21.0"
    assert normalize_tag("1.21.0") == "1.21.0"


def test_is_newer_compares_semver() -> None:
    assert is_newer("1.22.0", "1.21.0") is True
    assert is_newer("1.21.0", "1.21.0") is False
    assert is_newer("1.20.9", "1.21.0") is False
    assert is_newer("v1.22.0", "1.21.0") is True


def test_exe_asset_url_picks_eqgm_exe() -> None:
    payload = _release_payload("v1.22.0")
    url = exe_asset_url(payload)
    assert url.endswith("EQGM-1.22.0.exe")
    assert is_allowed_download_url(url)
    assert not is_allowed_download_url("https://example.com/EQGM-1.22.0.exe")


def test_check_for_updates_latest(monkeypatch) -> None:
    payload = _release_payload("v1.21.0")

    def fake_fetch() -> dict:
        return payload

    monkeypatch.setattr("inventory_parser.app_updates._fetch_latest_payload", fake_fetch)
    result = check_for_updates("1.21.0")
    assert result["ok"] is True
    assert result["status"] == "latest"
    assert result["message"] == "You have the latest version."


def test_check_for_updates_newer_release(monkeypatch) -> None:
    payload = _release_payload("v1.22.0")

    def fake_fetch() -> dict:
        return payload

    monkeypatch.setattr("inventory_parser.app_updates._fetch_latest_payload", fake_fetch)
    result = check_for_updates("1.21.0")
    assert result["ok"] is True
    assert result["status"] == "update"
    assert result["latest"] == "1.22.0"
    assert result["downloadUrl"].endswith("EQGM-1.22.0.exe")


def test_check_for_updates_fetch_error(monkeypatch) -> None:
    def boom() -> dict:
        raise TimeoutError("timed out")

    monkeypatch.setattr("inventory_parser.app_updates._fetch_latest_payload", boom)
    result = check_for_updates("1.21.0")
    assert result["ok"] is False
    assert result["status"] == "error"
    assert "timed out" in result["message"]


def test_open_update_download_rejects_foreign_url() -> None:
    api = WebApi()
    result = api.open_update_download("https://example.com/EQGM-1.22.0.exe")
    assert result["ok"] is False


def test_open_update_download_opens_github_url() -> None:
    api = WebApi()
    url = f"{DOWNLOAD_URL_PREFIX}releases/download/v1.22.0/EQGM-1.22.0.exe"
    with patch("inventory_parser.web_api.webbrowser.open") as open_browser:
        result = api.open_update_download(url)
    assert result["ok"] is True
    open_browser.assert_called_once_with(url)


def test_check_for_updates_api_delegates(monkeypatch) -> None:
    monkeypatch.setattr(
        "inventory_parser.web_api.fetch_app_updates",
        lambda: {"ok": True, "status": "latest", "current": "1.21.0"},
    )
    api = WebApi()
    result = api.check_for_updates()
    assert result["status"] == "latest"


def test_sample_github_json_roundtrip() -> None:
    raw = json.dumps(_release_payload("v9.9.9"))
    payload = json.loads(raw)
    assert exe_asset_url(payload).endswith("EQGM-9.9.9.exe")
