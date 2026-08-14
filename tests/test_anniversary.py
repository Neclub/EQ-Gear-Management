"""Tests for anniversary Distant Echoes gem filtering."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.slot2_augs.anniversary import (
    filter_anniversary_augs,
    is_anniversary_aug,
)
from inventory_parser.slot2_augs.build import build_slot2_export
from inventory_parser.slot2_augs.raidloot import AugCandidate, parse_raidloot_html
from inventory_parser.team_report import build_team_report

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "raidloot_dex_sample.html"


def _aug(name: str, item_id: int = 1) -> AugCandidate:
    return AugCandidate(
        item_id=item_id,
        name=name,
        profile="dex",
        focus_heroic=50,
    )


def _team(tmp_path: Path):
    inv = tmp_path / "Proglub_test-ROG-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Head\tTest Helm\t1\t1\t6\n"
        "Head-Slot2\tEmpty\t0\t0\t0\n",
        encoding="utf-8",
    )
    return build_team_report([inv])


def test_is_anniversary_aug_matches_gem_of_distant_echoes():
    assert is_anniversary_aug("Unparalleled Finesse Gem of Distant Echoes")
    assert is_anniversary_aug("Superlative Finesse Gem of Distant Echoes")
    assert not is_anniversary_aug("Unparalleled Stone of Distant Echoes")
    assert not is_anniversary_aug("Unparalleled Adroit Shard of Distant Echoes")
    assert not is_anniversary_aug("Acrobat's Gem of Unraveling Order")
    assert not is_anniversary_aug(None)


def test_filter_anniversary_augs_default_excludes():
    augs = [
        _aug("Acrobat's Gem of Unraveling Order", 175572),
        _aug("Unparalleled Finesse Gem of Distant Echoes", 166898),
        _aug("Joy of the Dancer", 175169),
    ]
    kept = filter_anniversary_augs(augs, include_anniversary=False)
    assert [a.item_id for a in kept] == [175572, 175169]
    assert filter_anniversary_augs(augs, include_anniversary=True) == augs


def test_export_bundle_excludes_anniversary_by_default(tmp_path: Path):
    html = FIXTURE.read_text(encoding="utf-8")
    bundle = build_slot2_export(
        _team(tmp_path),
        catalog_html=html,
        fetch_eqr_augs=False,
        fetch_chest_class=False,
        fetch_expansions=False,
        include_anniversary=False,
        type78_slot_by_parent_id={1: 2},
    )
    assert bundle.include_anniversary is False
    assert all(not is_anniversary_aug(a.name) for a in bundle.ranked_augs)
    assert all(not is_anniversary_aug(a.name) for a in bundle.catalog.augs)


def test_export_bundle_includes_anniversary_when_enabled(tmp_path: Path):
    html = FIXTURE.read_text(encoding="utf-8")
    full = parse_raidloot_html(html, "dex")
    assert any(is_anniversary_aug(a.name) for a in full)

    bundle = build_slot2_export(
        _team(tmp_path),
        catalog_html=html,
        fetch_eqr_augs=False,
        fetch_chest_class=False,
        fetch_expansions=False,
        include_anniversary=True,
        type78_slot_by_parent_id={1: 2},
    )
    assert bundle.include_anniversary is True
    assert any(is_anniversary_aug(a.name) for a in bundle.catalog.augs)
