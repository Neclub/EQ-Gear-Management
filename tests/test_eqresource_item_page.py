"""EQ Resource item pages are downloaded once and reused by item id."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
_ITEM_HTML = '<font size="+1"><b><center>Odd Bow<br>'


def _patch_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = lambda: tmp_path  # noqa: E731
    monkeypatch.setattr("inventory_parser.slot2_augs.paths.appdata_dir", target)
    monkeypatch.setattr("inventory_parser.eqresource_item_page.appdata_dir", target)
    monkeypatch.setattr("inventory_parser.slot2_augs.eqresource_augs.appdata_dir", target)
    monkeypatch.setattr(
        "inventory_parser.slot2_augs.eqresource_gear_tier.appdata_dir", target
    )
    monkeypatch.setattr("inventory_parser.raid_bis.catalog.appdata_dir", target)


def test_item_page_is_saved_and_reused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from inventory_parser.eqresource_item_page import (
        get_eqresource_item_html,
        item_page_path,
    )

    _patch_appdata(monkeypatch, tmp_path)
    calls = {"n": 0}

    def fake_get(url: str, **_kwargs: object) -> str:
        calls["n"] += 1
        assert "id=151787" in url
        return _ITEM_HTML

    monkeypatch.setattr("inventory_parser.eqresource_item_page.http_get_text", fake_get)
    assert get_eqresource_item_html(151787) == _ITEM_HTML
    assert get_eqresource_item_html(151787) == _ITEM_HTML
    assert calls["n"] == 1
    assert item_page_path(151787).is_file()


def test_error_page_is_not_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from inventory_parser.eqresource_item_page import (
        get_eqresource_item_html,
        item_page_path,
    )

    _patch_appdata(monkeypatch, tmp_path)
    calls = {"n": 0}

    def fake_get(_url: str, **_kwargs: object) -> str:
        calls["n"] += 1
        return "<html>database error</html>"

    monkeypatch.setattr("inventory_parser.eqresource_item_page.http_get_text", fake_get)
    assert "database error" in (get_eqresource_item_html(151787) or "")
    assert not item_page_path(151787).exists()
    get_eqresource_item_html(151787)
    assert calls["n"] == 2


def test_clear_cache_deletes_item_pages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from inventory_parser.eqresource_item_page import item_page_path
    from inventory_parser.slot2_augs.paths import ITEM_PAGE_DIRNAME, clear_disk_caches

    _patch_appdata(monkeypatch, tmp_path)
    path = item_page_path(151787)
    path.parent.mkdir(parents=True)
    path.write_text(_ITEM_HTML, encoding="utf-8")
    result = clear_disk_caches()
    assert result["ok"] is True
    assert ITEM_PAGE_DIRNAME in result["deleted"]
    assert not path.exists()


def test_old_aug_page_is_not_downloaded_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from inventory_parser.eqresource_item_page import item_page_path
    from inventory_parser.slot2_augs.eqresource_augs import (
        cache_path,
        resolve_eqresource_augs,
    )

    _patch_appdata(monkeypatch, tmp_path)
    html = (FIXTURES / "eqresource_aug_175572.html").read_text(encoding="utf-8")
    page = item_page_path(153970)
    page.parent.mkdir(parents=True)
    page.write_text(html, encoding="utf-8")
    cache_path().write_text(
        json.dumps(
            {
                "int:153970": {
                    "ok": False,
                    "fetched_at": "2026-01-01T00:00:00+00:00",
                }
            }
        ),
        encoding="utf-8",
    )

    def boom(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("saved item page must not hit EQ Resource")

    monkeypatch.setattr("inventory_parser.eqresource_item_page.http_get_text", boom)
    found = resolve_eqresource_augs([153970], "int", allow_network=True)
    assert found[153970].name == "Acrobat's Gem of Unraveling Order"


def test_range_gear_page_is_not_downloaded_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from inventory_parser.eqresource_item_page import item_page_path
    from inventory_parser.slot2_augs.eqresource_gear_tier import resolve_item_gear_tiers

    _patch_appdata(monkeypatch, tmp_path)
    html = (FIXTURES / "eqresource_chest_175821_pal.html").read_text(encoding="utf-8")
    page = item_page_path(153970)
    page.parent.mkdir(parents=True)
    page.write_text(html, encoding="utf-8")

    def boom(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("saved item page must not hit EQ Resource")

    monkeypatch.setattr("inventory_parser.eqresource_item_page.http_get_text", boom)
    resolved = resolve_item_gear_tiers([153970], allow_network=True)
    assert resolved[153970] == "SOR-R2"


def test_hydrate_uses_saved_page_when_item_cache_is_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from inventory_parser.eqresource_item_page import item_page_path
    from inventory_parser.raid_bis.catalog import (
        ITEM_CACHE_VERSION,
        _hydrate_items,
        item_cache_path,
    )
    from inventory_parser.raid_bis.models import RaidGearCandidate

    _patch_appdata(monkeypatch, tmp_path)
    html = (FIXTURES / "eqresource_item_inspect_175821.html").read_text(encoding="utf-8")
    page = item_page_path(151787)
    page.parent.mkdir(parents=True)
    page.write_text(html, encoding="utf-8")
    item_cache_path().write_text(
        json.dumps(
            {
                "_version": ITEM_CACHE_VERSION,
                "151787": {
                    "ok": True,
                    "classes": None,
                    "class_all": False,
                    "item": {
                        "item_id": 151787,
                        "name": "Item 151787",
                        "stats": {},
                        "classes": None,
                        "slots": [],
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    def boom(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("saved item page must not hit EQ Resource")

    monkeypatch.setattr("inventory_parser.eqresource_item_page.http_get_text", boom)
    monkeypatch.setattr("inventory_parser.raid_bis.catalog._http_get", boom)
    hydrated = _hydrate_items(
        [RaidGearCandidate(item_id=151787, name="Item 151787")],
        item_html_by_id={},
        allow_network=True,
        polite_delay_s=0,
    )
    assert hydrated[151787].name == "Exarch Breastplate of Resonant Fracture"
