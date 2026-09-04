import urllib.error

import pytest

from inventory_parser.http_fetch import http_get_text, http_post_text, is_png


def test_http_get_rejects_non_https() -> None:
    with pytest.raises(urllib.error.URLError):
        http_get_text(
            "http://items.eqresource.com/items.php?id=1",
            timeout=1,
            user_agent="EQGM-test",
        )


def test_http_get_rejects_foreign_host() -> None:
    with pytest.raises(urllib.error.URLError):
        http_get_text("https://example.com/", timeout=1, user_agent="EQGM-test")


def test_http_post_rejects_userinfo() -> None:
    with pytest.raises(urllib.error.URLError):
        http_post_text(
            "https://evil@items.eqresource.com/items.php",
            {"q": "1"},
            timeout=1,
            user_agent="EQGM-test",
        )


def test_is_png_accepts_small_png_header() -> None:
    assert is_png(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    assert not is_png(b"<html>not a png</html>")
    assert not is_png(b"\x89PNG\r\n\x1a\n" + b"\x00" * 300_000)
    assert not is_png(b"")


def test_load_icon_png_rejects_non_png_cache(tmp_path, monkeypatch) -> None:
    from inventory_parser.raid_bis import icons as icon_mod

    monkeypatch.setattr(icon_mod, "icon_cache_dir", lambda: tmp_path)
    junk = tmp_path / "5297.png"
    junk.write_bytes(b"<html>not an icon</html>")
    assert icon_mod._load_icon_png("5297", allow_network=False) is None
    assert icon_mod._load_icon_png("not-digits", allow_network=False) is None
