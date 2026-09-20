"""Tests for seeding AppData from the EQGM-Web GitHub prebuilt cache."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

from inventory_parser.prebuilt_cache import (
    META_FILENAME,
    SeedResult,
    apply_zip_to_appdata,
    merge_catalog_file,
    merge_map_cache,
    seed_prebuilt_cache,
)
from inventory_parser.raid_bis.catalog import ITEM_CACHE_VERSION
from inventory_parser.raid_bis.icons import resolve_icon_png_path
from inventory_parser.slot2_augs.paths import clear_disk_caches


PNG_MIN = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8


def _make_cache_zip(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for rel, data in members.items():
            zf.writestr(f"EQGM-Web-main/cache/{rel}", data)
    return buf.getvalue()


def test_merge_map_local_wins() -> None:
    local = {"1": {"ok": True, "name": "Local"}, "2": {"ok": True}}
    remote = {"1": {"ok": True, "name": "Remote"}, "3": {"ok": True}}
    merged = merge_map_cache(local, remote)
    assert merged["1"]["name"] == "Local"
    assert "2" in merged and "3" in merged


def test_merge_raid_bis_item_skips_wrong_version() -> None:
    local = {"1": {"ok": True}, "_version": ITEM_CACHE_VERSION}
    remote = {"2": {"ok": True}, "_version": ITEM_CACHE_VERSION - 1}
    merged = merge_map_cache(local, remote, require_item_version=True)
    assert "2" not in merged
    assert merged["1"]["ok"] is True


def test_merge_catalog_prefers_newer_fetched_at() -> None:
    local = {"fetched_at": "2026-01-01T00:00:00+00:00", "rows": [1]}
    remote = {"fetched_at": "2026-09-01T00:00:00+00:00", "rows": [2]}
    assert merge_catalog_file(local, remote, profile_keyed=False)["rows"] == [2]
    assert merge_catalog_file(remote, local, profile_keyed=False)["rows"] == [2]


def test_merge_profile_catalog_per_key() -> None:
    local = {
        "dex": {"fetched_at": "2026-09-01T00:00:00+00:00", "augs": [1]},
        "wis": {"fetched_at": "2026-01-01T00:00:00+00:00", "augs": [2]},
    }
    remote = {
        "dex": {"fetched_at": "2026-01-01T00:00:00+00:00", "augs": [9]},
        "wis": {"fetched_at": "2026-09-01T00:00:00+00:00", "augs": [8]},
        "shield": {"fetched_at": "2026-09-01T00:00:00+00:00", "augs": [7]},
    }
    merged = merge_catalog_file(local, remote, profile_keyed=True)
    assert merged["dex"]["augs"] == [1]
    assert merged["wis"]["augs"] == [8]
    assert merged["shield"]["augs"] == [7]


def test_apply_zip_merges_json_and_copies_sharded_icon(tmp_path: Path) -> None:
    (tmp_path / "eqresource_aug_cache.json").write_text(
        json.dumps({"1": {"ok": True, "name": "KeepMe"}}),
        encoding="utf-8",
    )
    zip_bytes = _make_cache_zip(
        {
            "eqresource_aug_cache.json": json.dumps(
                {"1": {"ok": True, "name": "Remote"}, "2": {"ok": True, "name": "New"}}
            ).encode("utf-8"),
            "item_icons/175/175913.png": PNG_MIN,
            "item_icons/expac-tol.jpg": b"\xff\xd8\xff" + b"\x00" * 8,
        }
    )
    result = apply_zip_to_appdata(zip_bytes, dest_root=tmp_path)
    assert result.ok is True
    assert "eqresource_aug_cache.json" in result.files_written
    data = json.loads((tmp_path / "eqresource_aug_cache.json").read_text(encoding="utf-8"))
    assert data["1"]["name"] == "KeepMe"
    assert data["2"]["name"] == "New"
    assert result.icons_copied == 2
    assert resolve_icon_png_path("175913", cache_dir=tmp_path / "item_icons") is not None
    assert (tmp_path / "item_icons" / "expac-tol.jpg").is_file()


def test_apply_zip_rejects_zip_slip(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("EQGM-Web-main/cache/../evil.json", b"{}")
        zf.writestr("EQGM-Web-main/cache/item_icons/../../outside.png", PNG_MIN)
    result = apply_zip_to_appdata(buf.getvalue(), dest_root=tmp_path)
    assert result.ok is True
    assert not (tmp_path / "evil.json").exists()
    assert not list(tmp_path.rglob("outside.png"))


def test_seed_skips_when_sha_matches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "inventory_parser.prebuilt_cache.appdata_dir",
        lambda: tmp_path,
    )
    (tmp_path / "eqresource_aug_cache.json").write_text("{}", encoding="utf-8")
    (tmp_path / META_FILENAME).write_text(
        json.dumps({"sha": "abc123"}),
        encoding="utf-8",
    )
    called = {"zip": False}

    def _sha() -> str:
        return "abc123"

    def _zip() -> bytes:
        called["zip"] = True
        return b""

    result = seed_prebuilt_cache(
        dest_root=tmp_path,
        fetch_sha=_sha,
        download_zip=_zip,
    )
    assert result.ok is True
    assert result.skipped is True
    assert result.reason == "up_to_date"
    assert called["zip"] is False


def test_seed_fail_open_on_network_error(tmp_path: Path) -> None:
    def _sha() -> str:
        raise OSError("offline")

    result = seed_prebuilt_cache(dest_root=tmp_path, fetch_sha=_sha)
    assert result.ok is False
    assert result.skipped is True
    assert result.error is not None


def test_seed_downloads_and_writes_meta(tmp_path: Path) -> None:
    zip_bytes = _make_cache_zip(
        {
            "item_class_cache.json": json.dumps(
                {"10": {"classes": ["WAR"], "fetched_at": "2026-09-01T00:00:00+00:00"}}
            ).encode("utf-8"),
            "item_icons/0/42.png": PNG_MIN,
        }
    )
    result = seed_prebuilt_cache(
        dest_root=tmp_path,
        fetch_sha=lambda: "sha-new",
        download_zip=lambda: zip_bytes,
    )
    assert result.ok is True
    assert result.skipped is False
    assert "item_class_cache.json" in result.files_written
    assert result.icons_copied == 1
    meta = json.loads((tmp_path / META_FILENAME).read_text(encoding="utf-8"))
    assert meta["sha"] == "sha-new"
    assert resolve_icon_png_path("42", cache_dir=tmp_path / "item_icons") is not None


def test_clear_cache_deletes_prebuilt_meta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "inventory_parser.slot2_augs.paths.appdata_dir",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "inventory_parser.prebuilt_cache.appdata_dir",
        lambda: tmp_path,
    )
    (tmp_path / "raid_bis_catalog.json").write_text("{}", encoding="utf-8")
    (tmp_path / META_FILENAME).write_text(json.dumps({"sha": "x"}), encoding="utf-8")
    result = clear_disk_caches()
    assert result["ok"] is True
    assert META_FILENAME in result["deleted"]
    assert not (tmp_path / META_FILENAME).exists()


def test_resolve_icon_prefers_sharded(tmp_path: Path) -> None:
    icons = tmp_path / "item_icons"
    sharded = icons / "1" / "1500.png"
    sharded.parent.mkdir(parents=True)
    sharded.write_bytes(PNG_MIN)
    flat = icons / "1500.png"
    flat.write_bytes(PNG_MIN)
    resolved = resolve_icon_png_path("1500", cache_dir=icons)
    assert resolved == sharded


def test_seed_result_dataclass_defaults() -> None:
    r = SeedResult(ok=True, skipped=True, reason="tests")
    assert r.files_written == []
    assert r.icons_copied == 0
