from pathlib import Path

from inventory_parser.achievement_report import AchievementReport, MissingCollectionRow
from inventory_parser.collection_drops import collection_drop_location
from inventory_parser.export_bundle import ExportBundle
from inventory_parser.html_export import (
    _collection_name_cell,
    extract_report_json,
    write_team_html,
)
from inventory_parser.team_report import TeamGearReport


def test_collection_drop_locations() -> None:
    assert collection_drop_location("Wellspring of the Shattering") == (
        "groundspawn - central area + feather area + geiger"
    )
    assert collection_drop_location("Relics of the Storm") == "dropped - linen butterflies"
    assert collection_drop_location("Relics of the Fallen Order") == "dropped - Undead"
    assert collection_drop_location("Flora of Hodstock Hills") == (
        "groundspawn - Typically Found All over, more common near water / trees"
    )


def test_collection_drop_name_folding_and_aliases() -> None:
    assert collection_drop_location("Don't be a Guppy") == "dropped - Ulthorks"
    assert collection_drop_location("Frosted Fakes?") == (
        "groundspawn - more toward beginning of zone"
    )
    assert collection_drop_location("Darkened Bones") == collection_drop_location(
        "Darkened Bonus"
    )
    assert collection_drop_location("Useless Tools") == "dropped - in mission – Vulak'Aerr"
    assert collection_drop_location("The Scars We Bear") is None


def test_html_export_includes_collection_drop(tmp_path: Path) -> None:
    bundle = ExportBundle(
        team=TeamGearReport(),
        achievement_report=AchievementReport(
            missing_collections=[
                MissingCollectionRow(
                    character="Shamlub",
                    expansion="Shattering of Ro",
                    zone="The Vortex",
                    collection="Relics of the Storm",
                    missing_item="Linen Butterfly",
                    progress="0/1",
                    char_has="",
                    total=1,
                ),
                MissingCollectionRow(
                    character="Shamlub",
                    expansion="Shattering of Ro",
                    zone="Scarred Grove",
                    collection="The Scars We Bear",
                    missing_item="Something",
                    progress="0/1",
                    char_has="",
                    total=1,
                ),
            ]
        ),
    )
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    text = out.read_text(encoding="utf-8")
    report = extract_report_json(text)
    missing = next(section for section in report["sections"] if section["id"] == "missing_collections")
    storm = next(row for row in missing["data"]["rows"] if row[3]["text"] == "Relics of the Storm")
    assert storm[3]["drop"] == "dropped - linen butterflies"
    scars = next(row for row in missing["data"]["rows"] if row[4] == "Something")
    assert scars[3] == "The Scars We Bear"
    assert "collection-drop" in text
    assert "drop-chip-balloon" in text


def test_collection_name_cell_includes_drop() -> None:
    assert _collection_name_cell("Relics of the Storm") == {
        "text": "Relics of the Storm",
        "drop": "dropped - linen butterflies",
    }
    assert _collection_name_cell("The Scars We Bear") == "The Scars We Bear"
