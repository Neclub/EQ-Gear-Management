"""Tests for curated useful-spell intersection with MissingSpells dumps."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from inventory_parser.excel_export import (
    GEAR_T_LEVEL_SHEET_NAME,
    MISSING_SPELLS_SHEET_NAME,
    MISSING_USEFUL_SPELLS_SHEET_NAME,
    RUNE_INVENTORY_SHEET_NAME,
    write_team_workbook,
)
from inventory_parser.export_bundle import ExportBundle, build_export_bundle
from inventory_parser.html_export import serialize_report
from inventory_parser.missing_spells import persona_key
from inventory_parser.team_report import CharacterGear, TeamGearReport, build_team_report
from inventory_parser.useful_spells import (
    UsefulSpell,
    build_missing_useful_spells_report,
    load_useful_spells,
    useful_matches_missing,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"


def test_load_useful_spells_has_shd_not_shk() -> None:
    catalog = load_useful_spells()
    assert "SHD" in catalog
    assert "SHK" not in catalog
    assert len(catalog["PAL"]) >= 40
    assert any(s.name == "Brilliant Expurgation" for s in catalog["PAL"])


def test_useful_matches_rk_iii_and_unranked() -> None:
    ranked = UsefulSpell(name="Brilliant Expurgation", level=130, highest_rk="III")
    assert useful_matches_missing(ranked, "Brilliant Expurgation Rk. III")
    assert useful_matches_missing(ranked, "Brilliant Expurgation Rk. II")
    assert not useful_matches_missing(ranked, "Some Other Spell Rk. III")

    unranked = UsefulSpell(name="Force of Revocation", level=130, highest_rk="n/a")
    assert useful_matches_missing(unranked, "Force of Revocation")


def test_useful_matches_numeric_rank() -> None:
    useful = UsefulSpell(name="Dichotomic Fury", level=101, highest_rk="6")
    assert useful_matches_missing(useful, "Dichotomic Fury VI")
    assert useful_matches_missing(useful, "Dichotomic Fury 6")
    assert not useful_matches_missing(useful, "Dichotomic Something Else VI")


def test_build_missing_useful_for_deflub_pal() -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    team = build_team_report(paths)
    report = build_missing_useful_spells_report(team, inventory_paths=paths)
    assert report is not None
    assert report.entries
    assert all(e.display_name == "Deflub ( PAL )" for e in report.entries)
    names = {e.spell_name for e in report.entries}
    assert any("Brilliant Expurgation" in n for n in names)
    # Lower-level useful spells from the dump are included (not 121–130 only)
    assert any(e.level < 121 for e in report.entries)


def test_excel_missing_useful_tab(tmp_path: Path) -> None:
    paths = sorted(EXAMPLES.glob("*-Inventory.txt"))
    bundle = build_export_bundle(paths, include_slot2=False)
    assert bundle.missing_useful_report is not None
    assert bundle.missing_useful_report.entries

    out = tmp_path / "useful.xlsx"
    write_team_workbook(
        bundle.team,
        out,
        spell_report=bundle.spell_report,
        missing_useful_report=bundle.missing_useful_report,
        rune_inventory_report=bundle.rune_inventory_report,
        unmade_entries=bundle.unmade_entries,
    )
    wb = load_workbook(out, data_only=True)
    assert MISSING_USEFUL_SPELLS_SHEET_NAME in wb.sheetnames
    # Sheet order: after Missing Spells, before Rune Inventory
    names = wb.sheetnames
    assert names.index(MISSING_SPELLS_SHEET_NAME) < names.index(MISSING_USEFUL_SPELLS_SHEET_NAME)
    assert names.index(MISSING_USEFUL_SPELLS_SHEET_NAME) < names.index(RUNE_INVENTORY_SHEET_NAME)

    ws = wb[MISSING_USEFUL_SPELLS_SHEET_NAME]
    header_row = next(
        r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == "Character"
    )
    assert [ws.cell(header_row, c).value for c in range(1, 7)] == [
        "Character",
        "Level",
        "Expansion",
        "Spell",
        "Current Rank",
        "Comments",
    ]
    assert ws.auto_filter.ref
    assert any(
        ws.cell(r, 1).value == "Deflub ( PAL )"
        for r in range(header_row + 1, ws.max_row + 1)
    )


def test_html_missing_useful_has_character_filter() -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    bundle = build_export_bundle(paths, include_slot2=False)
    payload = serialize_report(bundle)
    section = next(s for s in payload["sections"] if s["id"] == "missing_useful_spells")
    assert section["title"] == MISSING_USEFUL_SPELLS_SHEET_NAME
    assert section["data"]["characterColumn"] == 0
    assert section["data"]["rows"]
    assert all(row[0] == "Deflub ( PAL )" for row in section["data"]["rows"])
    credit = section["data"]["credit"]
    assert credit["text"] == 'Based on "SOR - Raccoo\'s list of useful spells"'
    assert "docs.google.com/spreadsheets" in credit["url"]
    expansions = {row[2] for row in section["data"]["rows"] if row[2]}
    assert "Shattering of Ro (2025)" in expansions
    assert not any(value in {"SOR", "TOB", "LS"} for value in expansions)
    spell_cells = [row[3] for row in section["data"]["rows"]]
    assert all(isinstance(cell, dict) and cell.get("url") for cell in spell_cells)
    brilliant = next(c for c in spell_cells if "Brilliant Expurgation" in c["text"])
    assert brilliant["url"] == "https://spells.eqresource.com/spells.php?id=71326"
    low_level = next(row for row in section["data"]["rows"] if row[1] < 121)
    assert "spells.eqresource.com" in low_level[3]["url"]


def test_excel_missing_useful_credit_hyperlink(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    bundle = build_export_bundle(paths, include_slot2=False)
    out = tmp_path / "useful_credit.xlsx"
    write_team_workbook(
        bundle.team,
        out,
        missing_useful_report=bundle.missing_useful_report,
    )
    wb = load_workbook(out, data_only=False)
    ws = wb[MISSING_USEFUL_SPELLS_SHEET_NAME]
    credit_row = next(
        r
        for r in range(1, ws.max_row + 1)
        if ws.cell(r, 1).value == 'Based on "SOR - Raccoo\'s list of useful spells"'
    )
    cell = ws.cell(credit_row, 1)
    assert cell.hyperlink is not None
    assert "docs.google.com/spreadsheets" in cell.hyperlink.target
    header_row = next(r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == "Character")
    spell_links = [
        ws.cell(r, 4).hyperlink.target
        for r in range(header_row + 1, ws.max_row + 1)
        if ws.cell(r, 4).hyperlink is not None
    ]
    assert spell_links
    assert any("spells.eqresource.com" in url for url in spell_links)
    assert any("spells.php?id=71326" in url for url in spell_links)


def _spell_dump(path: Path, lines: list[tuple[int, str]]) -> Path:
    path.write_text("".join(f"{level}\t{name}\n" for level, name in lines), encoding="utf-8")
    return path


def _spell_cell_text(cell: object) -> str:
    if isinstance(cell, dict):
        return str(cell.get("text", ""))
    return str(cell)


def test_missing_useful_rows_follow_the_spell_log(tmp_path: Path) -> None:
    """HTML and Excel list the MissingSpells line, not an older or mistyped name."""
    brd = _spell_dump(
        tmp_path / "Songlub_bristle-BRD-MissingSpells.txt",
        [
            (130, "Sorrowful Song of Suffering IX"),
            (127, "Cutting Insult X"),
            (125, "Covariance of Sticks and Stones Rk. III"),
            (85, "Wave of Slumber Rk. II"),
        ],
    )
    clr = _spell_dump(
        tmp_path / "Healub_bristle-CLR-MissingSpells.txt",
        [
            (129, "Unyielding Denunciation Rk. III"),
            (128, "Eminent Intervention Rk. III"),
            (129, "Word of Replenishment XIII Rk. III"),
        ],
    )
    shd = _spell_dump(
        tmp_path / "Deflub_bristle-SHD-MissingSpells.txt",
        [
            (89, "Insidious Blight Rk. II"),
            (129, "Insidious Blight IX"),
        ],
    )
    ber = _spell_dump(
        tmp_path / "Slamlub_bristle-BER-MissingSpells.txt",
        [(98, "Festering Rage Rk. II")],
    )
    war = _spell_dump(
        tmp_path / "Tanklub_bristle-WAR-MissingSpells.txt",
        [
            (120, "Levincrash Defense Discipline Rk. III"),
            (97, "Weapon Covenant Rk. II"),
            (101, "Dichotomic Fury VI"),
            (90, "Dichotomic Fury"),
            (129, "Opportunistic Strike IX Rk. III"),
            (78, "Opportunistic Strike Rk. II"),
        ],
    )
    mag = _spell_dump(
        tmp_path / "Magelub_bristle-MAG-MissingSpells.txt",
        [
            (121, "Burnout XVI Rk. III"),
            (126, "Burnout XVII Rk. III"),
        ],
    )
    files = {
        ("Songlub", "BRD"): brd,
        ("Healub", "CLR"): clr,
        ("Deflub", "SHD"): shd,
        ("Slamlub", "BER"): ber,
        ("Tanklub", "WAR"): war,
        ("Magelub", "MAG"): mag,
    }
    characters = [
        CharacterGear(
            character=character,
            server="bristle",
            filepath=str(path),
            class_abbr=class_abbr,
        )
        for (character, class_abbr), path in files.items()
    ]
    team = TeamGearReport(characters=characters)
    spell_paths = {
        persona_key(character, "bristle", class_abbr): path
        for (character, class_abbr), path in files.items()
    }
    useful_by_class = {
        "BRD": [
            UsefulSpell("Sorrowful Song of Suffering", 130, "SOR", "III"),
            UsefulSpell("Cutting Insult", 127, "SOR", "III"),
            UsefulSpell("Covariance of Stick's and Stones", 125, "SOR", "III"),
            UsefulSpell("Wave of Slumber X", 130, "SOR", "III"),
        ],
        "CLR": [
            UsefulSpell("Unyielding Demunication", 129, "SOR", "III"),
            UsefulSpell("Emninent Intervention", 128, "SOR", "III"),
            UsefulSpell("Word of of Replenishment XIII", 129, "SOR", "III"),
        ],
        "SHD": [UsefulSpell("Insidious Blight", 129, "SOR", "III")],
        "BER": [UsefulSpell("Festering Rage", 127, "SOR", "III")],
        "WAR": [
            UsefulSpell("Levincrash Defense Disc", 120, "TOV", "III"),
            UsefulSpell("Weapon Covenant", 97, "SOM", "III"),
            UsefulSpell("Dichotomic Fury", 101, "TBM", "6"),
            UsefulSpell("Opportunistic Strike IX", 130, "SOR", "III"),
        ],
        "MAG": [UsefulSpell("Burnout XVI", 126, "SOR", "III")],
    }
    report = build_missing_useful_spells_report(
        team,
        spell_paths=spell_paths,
        useful_by_class=useful_by_class,
    )
    assert report is not None
    reported = {
        (entry.display_name, entry.level, entry.spell_name, entry.current_rank)
        for entry in report.entries
    }
    expected = {
        ("Songlub ( BRD )", 130, "Sorrowful Song of Suffering IX", "Missing"),
        ("Songlub ( BRD )", 127, "Cutting Insult X", "Missing"),
        ("Songlub ( BRD )", 125, "Covariance of Sticks and Stones", "Rk. II"),
        ("Healub ( CLR )", 129, "Unyielding Denunciation", "Rk. II"),
        ("Healub ( CLR )", 128, "Eminent Intervention", "Rk. II"),
        ("Healub ( CLR )", 129, "Word of Replenishment XIII", "Rk. II"),
        ("Deflub ( SHD )", 129, "Insidious Blight IX", "Missing"),
        ("Tanklub ( WAR )", 120, "Levincrash Defense Discipline", "Rk. II"),
        ("Tanklub ( WAR )", 97, "Weapon Covenant", "Rk. I"),
        ("Tanklub ( WAR )", 101, "Dichotomic Fury VI", "Missing"),
        ("Tanklub ( WAR )", 129, "Opportunistic Strike IX", "Rk. II"),
        ("Magelub ( MAG )", 121, "Burnout XVI", "Rk. II"),
    }
    assert reported == expected

    payload = serialize_report(ExportBundle(team=team, missing_useful_report=report))
    section = next(item for item in payload["sections"] if item["id"] == "missing_useful_spells")
    html_rows = {
        (row[0], row[1], _spell_cell_text(row[3]), row[4]) for row in section["data"]["rows"]
    }

    workbook_path = tmp_path / "useful.xlsx"
    write_team_workbook(team, workbook_path, missing_useful_report=report, unmade_entries=[])
    worksheet = load_workbook(workbook_path, data_only=True)[MISSING_USEFUL_SPELLS_SHEET_NAME]
    header_row = next(
        row for row in range(1, worksheet.max_row + 1) if worksheet.cell(row, 1).value == "Character"
    )
    excel_rows: set[tuple[str, int, str, str]] = set()
    for row in range(header_row + 1, worksheet.max_row + 1):
        character = worksheet.cell(row, 1).value
        level = worksheet.cell(row, 2).value
        spell = worksheet.cell(row, 4).value
        current_rank = worksheet.cell(row, 5).value
        if (
            not isinstance(character, str)
            or not isinstance(level, int)
            or not isinstance(spell, str)
            or not isinstance(current_rank, str)
        ):
            continue
        excel_rows.add((character, level, spell, current_rank))

    assert html_rows == expected
    assert excel_rows == expected


def test_no_useful_tab_without_entries(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Stablub_bristle-Inventory.txt"]
    team = build_team_report(paths)
    out = tmp_path / "no_useful.xlsx"
    write_team_workbook(team, out)
    wb = load_workbook(out, data_only=True)
    assert MISSING_USEFUL_SPELLS_SHEET_NAME not in wb.sheetnames
    assert GEAR_T_LEVEL_SHEET_NAME in wb.sheetnames
