"""Tests for EQ Resource fallback T-codes on unknown equipped items."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.items import EquippedItem
from inventory_parser.slot2_augs.eqresource_gear_tier import parse_gear_tier_from_eqr_html
from inventory_parser.sor_tier import equipped_tier_label, sor_gap_label
from inventory_parser.team_report import CharacterGear, TeamGearReport

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_eqr_raid_tier_two_chest() -> None:
    html = (FIXTURES / "eqresource_chest_175821_pal.html").read_text(encoding="utf-8")
    assert parse_gear_tier_from_eqr_html(html) == "SOR-R2"


def test_parse_eqr_group_tier_three_aug() -> None:
    html = (FIXTURES / "eqresource_aug_175572.html").read_text(encoding="utf-8")
    assert parse_gear_tier_from_eqr_html(html) == "SOR-G3"


def test_parse_eqr_unmapped_expansion_stays_unknown() -> None:
    html = """
    <img src="expacimages/tol.jpg">
    <br><center>Raid - Tier 2</center>
    """
    assert parse_gear_tier_from_eqr_html(html) is None


def test_sor_gap_label_uses_resolved_tier() -> None:
    name = "Radiant Protector's Collar of Legacies Lost"
    assert sor_gap_label(name) == "???"
    assert sor_gap_label(name, resolved_tier="SOR-R2") == "SOR-R2"
    assert sor_gap_label(name, is_evolver=True, resolved_tier="SOR-R2") == "Evolver"
    assert (
        sor_gap_label("Bo Staff of Resonant Fracture", resolved_tier="TOB-R2")
        == "SOR-R2"
    )


def test_export_bundle_assigns_eqr_tier_for_unknown_item(tmp_path: Path) -> None:
    inv = tmp_path / "Unknownlub_test-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Neck\tRadiant Protector's Collar of Legacies Lost\t175821\t1\t6\n",
        encoding="utf-8",
    )
    html = (FIXTURES / "eqresource_chest_175821_pal.html").read_text(encoding="utf-8")
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        fetch_eqr_gear_tiers=True,
        eqr_gear_tier_html={175821: html},
        fetch_chest_class=False,
    )
    item = bundle.team.characters[0].slots["Neck"]
    assert equipped_tier_label(item) == "SOR-R2"
    assert item.resolved_tier == "SOR-R2"


def test_apply_skips_named_tiers() -> None:
    from inventory_parser.slot2_augs.eqresource_gear_tier import (
        apply_resolved_gear_tiers_to_team,
    )

    item = EquippedItem(
        name="Bo Staff of Resonant Fracture",
        item_id=175821,
    )
    team = TeamGearReport(
        characters=[
            CharacterGear(
                character="Named",
                server="test",
                filepath="x",
                slots={"Primary": item},
            )
        ]
    )
    html = (FIXTURES / "eqresource_chest_175821_pal.html").read_text(encoding="utf-8")
    apply_resolved_gear_tiers_to_team(
        team,
        html_overrides={175821: html},
        allow_network=False,
    )
    assert team.characters[0].slots["Primary"].resolved_tier is None
    assert equipped_tier_label(team.characters[0].slots["Primary"]) == "SOR-R2"
