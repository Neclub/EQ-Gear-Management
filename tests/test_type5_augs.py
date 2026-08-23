"""Tests for Type 5 aug display export."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from inventory_parser.excel_export import write_team_workbook
from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.html_export import serialize_report
from inventory_parser.type5_augs.build import TYPE5_CATALOG_URL
from inventory_parser.type5_augs.excel import SHEET_NAME
from inventory_parser.type5_augs.html import serialize_type5_section

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_include_type5_false_omits_section_and_sheet(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        include_type5=False,
    )
    assert bundle.type5 is None
    payload = serialize_report(bundle)
    assert all(s["type"] != "type5_augs" for s in payload["sections"])
    out = tmp_path / "no_type5.xlsx"
    write_team_workbook(bundle.team, out, type5=None)
    assert SHEET_NAME not in load_workbook(out).sheetnames


def test_include_type5_offline_adds_section(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    aug_html = (FIXTURES / "eqresource_aug_173378.html").read_text(encoding="utf-8")
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        include_type5=True,
        type5_slot_by_parent_id={},
        type5_fetch_eqr_augs=False,
        type5_eqr_aug_html_by_id={173378: aug_html},
        fetch_chest_class=False,
    )
    assert bundle.type5 is not None
    payload = serialize_report(bundle)
    section = next(s for s in payload["sections"] if s["type"] == "type5_augs")
    assert section["title"] == "Type 5 Augs"
    assert section["data"]["catalogUrl"] == TYPE5_CATALOG_URL

    data = serialize_type5_section(bundle.type5)
    assert "rows" in data
    assert data["eqResourceItemUrl"]

    out = tmp_path / "with_type5.xlsx"
    write_team_workbook(bundle.team, out, type5=bundle.type5)
    assert SHEET_NAME in load_workbook(out).sheetnames


def test_type5_html_template_has_per_character_cards() -> None:
    from inventory_parser.package_data import read_data_text

    html = read_data_text("team_report.html")
    assert "function updateType5AugsContent" in html
    assert "raidBisCharTitle(ch)" in html
    assert "type5PersonaKey" in html
    assert "empty of" in html
    assert ".type5-augs .card" in html
    assert ".type5-augs .card-head" in html
    assert "raid-bis-char-plate" in html


def test_type5_serialize_empty_and_stats() -> None:
    from inventory_parser.parser import InventoryData, InventoryItem
    from inventory_parser.team_report import CharacterGear, TeamGearReport
    from inventory_parser.type5_augs.build import build_type5_export

    data = InventoryData(
        character="Tester",
        server="bristle",
        filepath="x",
        class_abbr="WAR",
        items=[
            InventoryItem("Head", "Helm of Tests", 175860, 1, 3),
            InventoryItem("Head-Slot1", "Immovable Green Gem", 173378, 1, 0),
            InventoryItem("Ear", "Earring A", 175914, 1, 4),
            InventoryItem("Ear-Slot2", "Empty", 0, 0, 0),
        ],
    )
    char = CharacterGear(
        character="Tester",
        server="bristle",
        filepath="x",
        class_abbr="WAR",
        inventory_data=data,
    )
    team = TeamGearReport(characters=[char], warnings=[])
    aug_html = (FIXTURES / "eqresource_aug_173378.html").read_text(encoding="utf-8")
    export = build_type5_export(
        team,
        type5_slot_by_parent_id={175860: 1, 175914: 2},
        eqr_aug_html_by_id={173378: aug_html},
        fetch_eqr_augs=False,
        fetch_expansions=False,
    )
    payload = serialize_type5_section(export)
    by_slot = {r["gearSlot"]: r for r in payload["rows"]}
    assert by_slot["Head"]["name"] == "Immovable Green Gem"
    assert by_slot["Head"]["empty"] is False
    assert by_slot["Head"]["expansion"] == "The Outer Brood"
    assert by_slot["Head"]["hsta"] == 135
    assert by_slot["Head"]["hstr"] == 41
    assert by_slot["Ear-1"]["empty"] is True
    assert by_slot["Ear-1"]["name"] is None
    assert by_slot["Ear-1"]["expansion"] is None
    assert payload["catalogUrl"] == TYPE5_CATALOG_URL
