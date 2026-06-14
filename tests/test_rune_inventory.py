"""Tests for inventory-based raid rune counts."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.rune_inventory import (
    build_rune_inventory_report,
    expected_item_name,
    is_rune_inventory_location,
    load_rune_inventory_config,
    tier_from_item_name,
)
from inventory_parser.team_report import build_team_report

EXAMPLES = Path(__file__).resolve().parent.parent / "Examples"


def test_is_rune_inventory_location() -> None:
    assert is_rune_inventory_location("General 1-Slot1")
    assert is_rune_inventory_location("Bank15-Slot4")
    assert is_rune_inventory_location("SharedBank3-Slot6")
    assert not is_rune_inventory_location("Chest-Slot2")
    assert not is_rune_inventory_location("Ear-1")


def test_tier_from_item_name_tob_prefix() -> None:
    config = load_rune_inventory_config()
    tob = next(f for f in config.families if f.id == "tob")
    assert tier_from_item_name("Energized Minor Engram", tob, config.tiers) == "Minor"
    assert tier_from_item_name("Inert Minor Engram", tob, config.tiers) is None
    assert tier_from_item_name("Covariant Engram", tob, config.tiers) is None


def test_healub_nos_symbol_counts() -> None:
    report = build_team_report([EXAMPLES / "Healub_bristle-Inventory.txt"])
    inv = build_rune_inventory_report(report)
    assert inv is not None
    healub = report.characters[0]
    nos = next(f for f in inv.families if f.id == "nos")
    counts = nos.counts[healub.persona_key]
    assert counts["Minor"] == 3
    assert counts["Lesser"] == 1
    assert counts["Median"] == 1
    assert counts["Greater"] == 1
    assert counts["Glowing"] == 0


def test_deflub_ls_tob_sor_counts() -> None:
    report = build_team_report([EXAMPLES / "Deflub_bristle-Inventory.txt"])
    inv = build_rune_inventory_report(report)
    assert inv is not None
    deflub = report.characters[0]
    ls = next(f for f in inv.families if f.id == "ls")
    tob = next(f for f in inv.families if f.id == "tob")
    sor = next(f for f in inv.families if f.id == "sor")
    assert ls.counts[deflub.persona_key]["Greater"] == 1
    assert tob.counts[deflub.persona_key]["Minor"] == 1
    assert tob.counts[deflub.persona_key]["Median"] == 1
    assert tob.counts[deflub.persona_key]["Greater"] == 1
    assert tob.counts[deflub.persona_key]["Glowing"] == 1
    assert sor.counts[deflub.persona_key]["Lesser"] == 1


def test_inert_and_covariant_engrams_excluded() -> None:
    report = build_team_report([EXAMPLES / "Deflub_bristle-Inventory.txt"])
    inv = build_rune_inventory_report(report)
    assert inv is not None
    deflub = report.characters[0]
    tob = next(f for f in inv.families if f.id == "tob")
    total_tob = sum(tob.counts[deflub.persona_key].values())
    assert total_tob == 4


def test_empty_team_returns_none() -> None:
    from inventory_parser.team_report import TeamGearReport

    empty = TeamGearReport(characters=[], warnings=[])
    assert build_rune_inventory_report(empty) is None


def test_expected_item_names() -> None:
    config = load_rune_inventory_config()
    nos = next(f for f in config.families if f.id == "nos")
    tob = next(f for f in config.families if f.id == "tob")
    assert expected_item_name("Minor", nos) == "Minor Symbol of Shar Vahl"
    assert expected_item_name("Minor", tob) == "Energized Minor Engram"
