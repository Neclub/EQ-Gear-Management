"""Tests for Hero's Special AAs catalog matching."""

from pathlib import Path

from inventory_parser.achievement_parser import parse_achievements_file
from inventory_parser.achievement_report import (
    _heroic_aa_rows_from_parse,
    _heroic_aa_totals_from_rows,
    build_achievement_report,
)
from inventory_parser.heroic_aas import load_heroic_aa_catalog, normalize_heroic_name
from inventory_parser.team_report import build_team_report

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
ACHIEVEMENTS = EXAMPLES / "Achievements"
SHAMLUB_ACH = ACHIEVEMENTS / "Shamlub_xegony-Achievements.txt"


def test_catalog_totals() -> None:
    catalog = load_heroic_aa_catalog()
    assert len(catalog.achievements) == 138
    assert catalog.max_fortitude == 114
    assert catalog.max_resolution == 57
    assert catalog.max_vitality == 114
    assert sum(item.fortitude for item in catalog.achievements) == 114
    assert sum(item.resolution for item in catalog.achievements) == 57
    assert sum(item.vitality for item in catalog.achievements) == 114
    assert catalog.credit_url.startswith("https://everquest.fanra.info/")
    assert any(ability.id == "fortitude" for ability in catalog.abilities)


def test_normalize_heroic_name_apostrophe_and_colon() -> None:
    dump = "Savior of The Hero's Forge: Heroes Are Forged"
    wiki = "Savior of The Hero's Forge:Heroes Are Forged"
    curly = "Savior of Stratos: Zephyr\u2019s Flight"
    straight = "Savior of Stratos: Zephyr's Flight"
    assert normalize_heroic_name(wiki) == normalize_heroic_name(dump)
    assert normalize_heroic_name(curly) == normalize_heroic_name(straight)
    assert normalize_heroic_name("Saviour of Gorowyn") == normalize_heroic_name(
        "Savior of Gorowyn"
    )


def test_fixture_dump_counts_completed_west_karana(tmp_path: Path) -> None:
    path = tmp_path / "Test_server-Achievements.txt"
    path.write_text(
        "Call of the Forsaken: General\n"
        "C\tSavior of West Karana\n"
        "I\tSavior of West Karana II\n",
        encoding="utf-8",
    )
    parsed = parse_achievements_file(path)
    assert any(
        item.name == "Savior of West Karana" and item.complete for item in parsed.top_level
    )
    rows = _heroic_aa_rows_from_parse("Tester", parsed.top_level, load_heroic_aa_catalog())
    west = next(row for row in rows if row.achievement == "Savior of West Karana (Ethernere)")
    west_ii = next(
        row for row in rows if row.achievement == "Savior of West Karana (Ethernere) II"
    )
    assert west.status == "Completed"
    assert west.fortitude == 1
    assert west.vitality == 1
    assert west_ii.status == "Incomplete"
    unmatched = next(
        row for row in rows if row.achievement == "Savior of The Hero's Forge: Heroes Are Forged"
    )
    assert unmatched.status == "Incomplete"
    totals = _heroic_aa_totals_from_rows(rows)
    assert len(totals) == 1
    assert totals[0].fortitude == 1
    assert totals[0].vitality == 1
    assert totals[0].completed == 1
    assert totals[0].total == 138


def test_live_dump_matches_known_heroic_names() -> None:
    parsed = parse_achievements_file(SHAMLUB_ACH)
    rows = _heroic_aa_rows_from_parse("Shamlub", parsed.top_level, load_heroic_aa_catalog())
    by_name = {row.achievement: row for row in rows}
    forged = by_name["Savior of The Hero's Forge: Heroes Are Forged"]
    assert forged.status == "Completed"
    assert forged.fortitude == 1
    assert forged.resolution == 1
    assert forged.vitality == 1
    west = by_name["Savior of West Karana (Ethernere)"]
    assert west.status == "Incomplete"
    zeal = by_name["Hero of Stratos: Zephyr's Flight"]
    assert zeal.status == "Completed"


def test_build_report_includes_heroic_rows() -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([inv])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    assert ach_report.heroic_aas
    assert ach_report.heroic_aa_totals
    assert ach_report.heroic_aa_totals[0].total == 138
    assert {row.status for row in ach_report.heroic_aas} <= {"Completed", "Incomplete"}


def test_colossus_does_not_award_resolution() -> None:
    catalog = load_heroic_aa_catalog()
    colossus = next(
        item
        for item in catalog.achievements
        if item.name == "Hero of Arcstone, Shattered Isles: Colossus"
    )
    assert colossus.fortitude == 1
    assert colossus.resolution == 0
    assert colossus.vitality == 1
    rows = _heroic_aa_rows_from_parse("Tester", [], catalog)
    row = next(r for r in rows if r.achievement == colossus.name)
    assert row.resolution == 0
    assert row.status == "Incomplete"


def test_html_skips_chips_for_unawarded_ranks() -> None:
    from inventory_parser.package_data import read_data_text

    html = read_data_text("team_report.html")
    assert "if (!awarded) return;" in html
    assert 'done ? "heroic-chip on" : "heroic-chip"' in html
