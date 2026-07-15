from pathlib import Path

from inventory_parser.achievement_files import (
    achievement_character_key,
    collect_achievement_paths,
    discover_achievements_files,
    is_achievements_file,
    parse_achievements_filename,
)
from inventory_parser.achievement_parser import (
    EVERQUEST_BASE_LABEL,
    format_expansion_label,
    parse_achievements_file,
    split_collection_name,
)
from inventory_parser.achievement_report import build_achievement_report
from inventory_parser.team_report import build_team_report
from inventory_parser.excel_export import (
    ACHIEVEMENT_SUMMARY_SHEET_NAME,
    MISSING_COLLECTIONS_SHEET_NAME,
    RAID_ACHIEVEMENTS_SHEET_NAME,
    write_team_workbook,
)
from inventory_parser.missing_spells import split_input_paths

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
ACHIEVEMENTS = EXAMPLES / "Achievements"
SHAMLUB_ACH = ACHIEVEMENTS / "Shamlub_xegony-Achievements.txt"


def test_is_achievements_file() -> None:
    assert is_achievements_file(SHAMLUB_ACH)
    assert not is_achievements_file(EXAMPLES / "Shamlub_bristle-Inventory.txt")


def test_parse_achievements_filename() -> None:
    assert parse_achievements_filename(SHAMLUB_ACH) == ("Shamlub", "xegony")
    assert achievement_character_key(SHAMLUB_ACH) == "Shamlub_xegony"


def test_split_input_paths_includes_achievements() -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    inventory_paths, spell_paths, achievement_paths = split_input_paths([inv, SHAMLUB_ACH])
    assert inventory_paths == [inv]
    assert spell_paths == []
    assert achievement_paths == [SHAMLUB_ACH]


def test_split_collection_name() -> None:
    collection, zone = split_collection_name("The Depths of Fear (Rain of Fear)")
    assert collection == "The Depths of Fear"
    assert zone == "Rain of Fear"


def test_parse_missing_collection_items() -> None:
    parsed = parse_achievements_file(SHAMLUB_ACH)
    missing = parsed.missing_collections
    assert missing
    strange = next(item for item in missing if item.item == "Strange Black Rock")
    assert strange.section == "Rain of Fear"
    assert strange.zone == "Rain of Fear"
    assert strange.collection == "The Depths of Fear"
    assert strange.owned == 0
    assert strange.total == 1


def test_section_summary_counts_top_level_achievements() -> None:
    parsed = parse_achievements_file(SHAMLUB_ACH)
    general = next(s for s in parsed.section_summaries if s.section == "General")
    assert general.completed > 0
    assert general.total == general.completed + general.incomplete


def test_discover_achievements_files() -> None:
    files = discover_achievements_files(ACHIEVEMENTS)
    assert SHAMLUB_ACH.resolve() in [p.resolve() for p in files]


def test_parse_missing_raid_achievements() -> None:
    parsed = parse_achievements_file(SHAMLUB_ACH)
    rain_fear = [
        raid for raid in parsed.missing_raid_achievements if raid.section == "Rain of Fear"
    ]
    assert rain_fear
    assert any(
        raid.raid == "Vanquisher of Vulak`Aerr" and raid.objective == "None Shall Pass"
        for raid in rain_fear
    )
    assert all(raid.objective for raid in parsed.missing_raid_achievements)
    assert all(raid.section for raid in parsed.missing_raid_achievements)


def test_raid_achievements_exclude_completed() -> None:
    parsed = parse_achievements_file(SHAMLUB_ACH)
    completed = {
        (raid.raid, raid.objective)
        for raid in parsed.missing_raid_achievements
        if raid.section == "Shattering of Ro"
        and raid.raid == "Conqueror of Candlemaker's Workshop: Waxwork Abolishion"
    }
    assert ("Conqueror of Candlemaker's Workshop: Waxwork Abolishion", "") not in completed


def test_format_expansion_label() -> None:
    assert format_expansion_label("Shattering of Ro") == "Shattering of Ro (2025)"
    assert format_expansion_label("Rain of Fear") == "Rain of Fear (2012)"
    assert format_expansion_label("EverQuest") == EVERQUEST_BASE_LABEL
    assert format_expansion_label("General") == "General"


def test_build_achievement_report_includes_sorted_raid_rows() -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([inv])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    assert ach_report.raid_achievements
    expansions = [format_expansion_label(row.expansion) for row in ach_report.raid_achievements]
    assert expansions.index("Shattering of Ro (2025)") < expansions.index("Rain of Fear (2012)")
    assert expansions.index("Rain of Fear (2012)") < expansions.index(EVERQUEST_BASE_LABEL)


def test_build_achievement_report_with_explicit_path() -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([inv])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    strange_row = next(
        row for row in ach_report.missing_collections if row.missing_item == "Strange Black Rock"
    )
    assert strange_row.char_has == ""
    assert any(row.section == "General" for row in ach_report.summaries)
    assert any(row.expansion == "Rain of Fear" for row in ach_report.raid_achievements)


def test_missing_collections_char_has_from_team_inventory(tmp_path: Path) -> None:
    holder_inv = tmp_path / "Tanklub_bristle-Inventory.txt"
    holder_inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "General1-Slot1\tStrange Black Rock\t12345\t1\t6\n",
        encoding="utf-8",
    )
    missing_inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([missing_inv, holder_inv])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    strange_row = next(
        row for row in ach_report.missing_collections if row.missing_item == "Strange Black Rock"
    )
    assert strange_row.char_has == "Tanklub"


def test_achievement_report_once_per_character_across_personas(tmp_path: Path) -> None:
    """Personas share achievements/collections — emit one row set per character."""
    pal_inv = tmp_path / "Shamlub_bristle-PAL-Inventory.txt"
    shd_inv = tmp_path / "Shamlub_bristle-SHD-Inventory.txt"
    pal_inv.write_text(
        "Location\tName\tID\tCount\tSlots\nHead\tPAL Helm\t1\t1\t0\n",
        encoding="utf-8",
    )
    shd_inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Head\tSHD Helm\t2\t1\t0\n"
        "General1-Slot1\tStrange Black Rock\t12345\t1\t6\n",
        encoding="utf-8",
    )
    report = build_team_report([pal_inv, shd_inv])
    assert len(report.characters) == 2

    parsed = parse_achievements_file(SHAMLUB_ACH)
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    assert len(ach_report.missing_collections) == len(parsed.missing_collections)
    assert len(ach_report.summaries) == len(
        [s for s in parsed.section_summaries if s.total > 0]
    )
    assert len(ach_report.raid_achievements) == len(parsed.missing_raid_achievements)
    assert {row.character for row in ach_report.missing_collections} == {"Shamlub"}
    assert {row.character for row in ach_report.summaries} == {"Shamlub"}
    assert {row.character for row in ach_report.raid_achievements} == {"Shamlub"}

    strange_row = next(
        row for row in ach_report.missing_collections if row.missing_item == "Strange Black Rock"
    )
    # Char Has lists the character once even when multiple persona dumps hold the item.
    assert strange_row.char_has == "Shamlub"


def test_char_has_dedupes_personas_of_holder(tmp_path: Path) -> None:
    holder_pal = tmp_path / "Tanklub_bristle-PAL-Inventory.txt"
    holder_shd = tmp_path / "Tanklub_bristle-SHD-Inventory.txt"
    for path in (holder_pal, holder_shd):
        path.write_text(
            "Location\tName\tID\tCount\tSlots\n"
            "General1-Slot1\tStrange Black Rock\t12345\t1\t6\n",
            encoding="utf-8",
        )
    missing_inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([missing_inv, holder_pal, holder_shd])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    strange_row = next(
        row for row in ach_report.missing_collections if row.missing_item == "Strange Black Rock"
    )
    assert strange_row.char_has == "Tanklub"


def test_collect_achievement_paths_from_achievementdata(tmp_path: Path) -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    data_dir = tmp_path / "AchievementData"
    data_dir.mkdir()
    copied = data_dir / "Shamlub_bristle-Achievements.txt"
    copied.write_text(SHAMLUB_ACH.read_text(encoding="utf-8"), encoding="utf-8")
    work_inv = tmp_path / inv.name
    work_inv.write_text(inv.read_text(encoding="utf-8"), encoding="utf-8")

    discovered = collect_achievement_paths([work_inv])
    assert discovered["shamlub_bristle"].resolve() == copied.resolve()


def test_achievement_sheets_in_workbook(tmp_path: Path) -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    report = build_team_report([inv])
    ach_report = build_achievement_report(
        report,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    out = tmp_path / "crew.xlsx"
    write_team_workbook(report, out, achievement_report=ach_report)

    from openpyxl import load_workbook

    wb = load_workbook(out, data_only=True)
    assert MISSING_COLLECTIONS_SHEET_NAME in wb.sheetnames
    assert ACHIEVEMENT_SUMMARY_SHEET_NAME in wb.sheetnames
    assert RAID_ACHIEVEMENTS_SHEET_NAME in wb.sheetnames
    missing_ws = wb[MISSING_COLLECTIONS_SHEET_NAME]
    assert missing_ws.cell(1, 5).value == "Missing Item"
    assert missing_ws.cell(1, 7).value == "Char Has"
    raid_ws = wb[RAID_ACHIEVEMENTS_SHEET_NAME]
    assert raid_ws.cell(1, 2).value == "Expansion"
    assert raid_ws.cell(2, 2).value == EVERQUEST_BASE_LABEL or " (20" in str(raid_ws.cell(2, 2).value)
    assert raid_ws.auto_filter.ref is not None
    assert any(
        missing_ws.cell(row, 5).value == "Strange Black Rock"
        for row in range(2, missing_ws.max_row + 1)
    )
