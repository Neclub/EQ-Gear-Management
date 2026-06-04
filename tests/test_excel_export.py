from pathlib import Path

from openpyxl import load_workbook

from inventory_parser.crew_report import build_crew_report
from inventory_parser.excel_export import GEAR_T_LEVEL_SHEET_NAME, UNMADE_GEAR_SHEET_NAME, write_crew_workbook
from inventory_parser.excel_theme import SHEET_BACKGROUND_COLS, SHEET_BACKGROUND_ROWS
from inventory_parser.spell_report import build_spell_rune_report
from inventory_parser.parser import extract_equipped_items, parse_inventory_file
from inventory_parser.slots import CREW_GEAR_SLOTS, VISIBLE_SLOTS

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
_FIRST_CHAR_COL = 3


def _read_matrix(path: Path) -> dict[str, dict[str, str | None]]:
    wb = load_workbook(path, data_only=True)
    ws = wb["Crew gear"]
    chars = [ws.cell(1, c).value for c in range(_FIRST_CHAR_COL, ws.max_column + 1)]
    out: dict[str, dict[str, str | None]] = {ch: {} for ch in chars if ch}
    for r in range(2, ws.max_row + 1):
        slot = ws.cell(r, 1).value
        if not slot:
            continue
        for c, ch in enumerate(chars, start=_FIRST_CHAR_COL):
            if not ch:
                continue
            out[ch][slot] = ws.cell(r, c).value
    return out


def test_slot_rows_visible_first(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    slots = [ws.cell(r, 1).value for r in range(2, 2 + len(CREW_GEAR_SLOTS))]
    assert slots == list(CREW_GEAR_SLOTS)
    assert slots[: len(VISIBLE_SLOTS)] == list(VISIBLE_SLOTS)
    assert ws.cell(2, 2).value == "Visible"
    assert ws.cell(2 + len(VISIBLE_SLOTS), 2).value == "Non-visible"


def test_deflub_arms_item_name(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    matrix = _read_matrix(out)
    assert matrix["Deflub ( PAL )"]["Arms"] == "Exarch Vambraces of Eternal Reverie"


def test_item_hyperlink_to_eqresource(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    charm_row = 2 + list(CREW_GEAR_SLOTS).index("Charm")
    cell = ws.cell(charm_row, _FIRST_CHAR_COL)
    assert cell.value == "Defender's Charm of Rebellion"
    assert cell.hyperlink is not None
    assert cell.hyperlink.target == "https://items.eqresource.com/items.php?id=173940"


def test_empty_secondary_left_blank(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Monklub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    matrix = _read_matrix(out)
    assert matrix["Monklub ( MNK )"].get("Secondary") in (None, "")


def test_matches_extract_equipped(tmp_path: Path) -> None:
    path = EXAMPLES / "Stablub_bristle-Inventory.txt"
    data = parse_inventory_file(path)
    assert data is not None
    equipped, _evolver_keys = extract_equipped_items(data)

    report = build_crew_report([path])
    out = tmp_path / "one.xlsx"
    write_crew_workbook(report, out)

    matrix = _read_matrix(out)
    for slot in CREW_GEAR_SLOTS:
        if slot in equipped:
            assert matrix["Stablub"].get(slot) == equipped[slot].name
            assert report.characters[0].slots[slot].item_id == equipped[slot].item_id
        else:
            assert matrix["Stablub"].get(slot) in (None, "")


def test_visible_only_export(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "visible.xlsx"
    write_crew_workbook(report, out, slot_filter="visible")

    wb = load_workbook(out, data_only=True)
    ws = wb["Crew gear"]
    slots = [ws.cell(r, 1).value for r in range(2, 2 + len(VISIBLE_SLOTS))]
    assert slots == list(VISIBLE_SLOTS)
    assert "Charm" not in slots


def test_includes_all_example_characters() -> None:
    paths = sorted(EXAMPLES.glob("*_bristle-Inventory.txt"))
    report = build_crew_report(paths)
    names = {r.character for r in report.characters}
    assert names == {
        "Deflub",
        "Healub",
        "Magelub",
        "Monklub",
        "Shamlub",
        "Songlub",
        "Stablub",
    }


def test_gear_legend_on_a26_a35(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    assert ws.cell(25, 1).value == "Gear sets (newest to oldest)"
    assert ws.cell(26, 1).fill.start_color.rgb in ("005C4688", "FF5C4688")
    assert "Evolver" in str(ws.cell(26, 2).value)
    assert ws.cell(27, 1).fill.start_color.rgb in ("003A3350", "FF3A3350")
    assert "Fracture" in str(ws.cell(27, 2).value)
    assert ws.cell(35, 1).fill.start_color.rgb in ("003A3935", "FF3A3935")
    assert "Luclinite Coagulated" in str(ws.cell(35, 2).value)


def test_black_background_to_row_50_column_z(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    corner = ws.cell(50, 26)
    assert corner.fill.start_color.rgb in ("00000000", "FF000000")
    assert ws.cell(25, 15).fill.start_color.rgb in ("00000000", "FF000000")


def test_no_excel_table_only_autofilter(tmp_path: Path) -> None:
    """Excel Table + worksheet autoFilter duplicates XML and triggers repair dialog."""
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    assert list(ws.tables.keys()) == []
    assert ws.auto_filter.ref is not None


def test_rebellion_cell_has_fill(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "crew.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=False)
    ws = wb["Crew gear"]
    charm_row = 2 + list(CREW_GEAR_SLOTS).index("Charm")
    charm_cell = ws.cell(charm_row, _FIRST_CHAR_COL)
    assert charm_cell.value == "Defender's Charm of Rebellion"
    assert charm_cell.fill.start_color.rgb in ("00542A35", "FF542A35")

    assert wb.sheetnames == ["Crew gear", GEAR_T_LEVEL_SHEET_NAME, UNMADE_GEAR_SHEET_NAME]


def _sor_slot_names(path: Path) -> list[str]:
    wb = load_workbook(path, data_only=True)
    ws = wb[GEAR_T_LEVEL_SHEET_NAME]
    return [
        ws.cell(r, 1).value
        for r in range(2, ws.max_row + 1)
        if ws.cell(r, 1).value and r < 25
    ]


def _sor_slot_row(path: Path, slot: str) -> int:
    wb = load_workbook(path, data_only=True)
    ws = wb[GEAR_T_LEVEL_SHEET_NAME]
    for row in range(2, ws.max_row + 1):
        if ws.cell(row, 1).value == slot:
            return row
    raise AssertionError(f"Slot {slot!r} not found on Gear T-Level sheet")


def test_sor_gaps_sheet_and_secondary_row(tmp_path: Path) -> None:
    report = build_crew_report([EXAMPLES / "Stablub_bristle-Inventory.txt"])
    out = tmp_path / "sor.xlsx"
    write_crew_workbook(report, out)
    assert GEAR_T_LEVEL_SHEET_NAME in load_workbook(out, data_only=True).sheetnames
    assert "Secondary" in _sor_slot_names(out)

    report2 = build_crew_report([EXAMPLES / "Monklub_bristle-Inventory.txt"])
    out2 = tmp_path / "sor2.xlsx"
    write_crew_workbook(report2, out2)
    assert "Secondary" not in _sor_slot_names(out2)


def test_sor_gaps_markers_on_deflub(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    out = tmp_path / "sor.xlsx"
    write_crew_workbook(build_crew_report(paths), out)

    wb = load_workbook(out, data_only=True)
    ws = wb[GEAR_T_LEVEL_SHEET_NAME]
    charm_row = _sor_slot_row(out, "Charm")
    assert ws.cell(charm_row, _FIRST_CHAR_COL).value == "TOB-R2"


def test_gear_t_level_sor_r2_on_deflub_fingers(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    out = tmp_path / "gear_t_level.xlsx"
    write_crew_workbook(build_crew_report(paths), out)

    wb = load_workbook(out, data_only=True)
    ws = wb[GEAR_T_LEVEL_SHEET_NAME]
    fingers_row = _sor_slot_row(out, "Fingers-2")
    assert ws.cell(fingers_row, _FIRST_CHAR_COL).value == "SOR-R2"


def test_sor_gaps_evolver_label(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    out = tmp_path / "sor_evolver.xlsx"
    write_crew_workbook(build_crew_report(paths), out)

    wb = load_workbook(out, data_only=True)
    ws = wb[GEAR_T_LEVEL_SHEET_NAME]
    ear2_row = _sor_slot_row(out, "Ear-2")
    assert ws.cell(ear2_row, _FIRST_CHAR_COL).value == "Evolver"


def test_spell_tabs_all_examples(tmp_path: Path) -> None:
    paths = sorted(EXAMPLES.glob("*-Inventory.txt"))
    crew = build_crew_report(paths)
    spell = build_spell_rune_report(crew, inventory_paths=paths)
    assert spell is not None
    out = tmp_path / "crew_spells.xlsx"
    write_crew_workbook(crew, out, spell_report=spell)

    wb = load_workbook(out, data_only=True)
    assert wb.sheetnames == [
        "Crew gear",
        GEAR_T_LEVEL_SHEET_NAME,
        "Missing Runes",
        "Spell List",
        UNMADE_GEAR_SHEET_NAME,
    ]
    assert wb["Missing Runes"]["A1"].value == "Missing Runes"
    ws = wb["Spell List"]
    detail_row = next(
        r
        for r in range(1, ws.max_row + 1)
        if ws.cell(r, 1).value == "Deflub ( PAL )" and ws.cell(r, 5).value == "Committal Rk. III"
    )
    assert ws.cell(detail_row, 3).value == 126
    assert ws.cell(detail_row, 4).value == "Minor"


def test_spell_list_black_background_through_z(tmp_path: Path) -> None:
    paths = sorted(EXAMPLES.glob("*-Inventory.txt"))
    crew = build_crew_report(paths)
    spell = build_spell_rune_report(crew, inventory_paths=paths)
    assert spell is not None
    out = tmp_path / "spell_bg.xlsx"
    write_crew_workbook(crew, out, spell_report=spell)

    wb = load_workbook(out, data_only=False)
    ws = wb["Spell List"]
    last_row = max(
        r
        for r in range(1, ws.max_row + 1)
        if any(ws.cell(r, c).value for c in range(1, 6))
    )
    assert last_row > SHEET_BACKGROUND_ROWS

    black = ("00000000", "FF000000")
    assert ws.cell(last_row, SHEET_BACKGROUND_COLS).fill.start_color.rgb in black
    assert ws.cell(last_row, 6).fill.start_color.rgb in black
    assert ws.cell(1, SHEET_BACKGROUND_COLS).fill.start_color.rgb in black


def test_character_class_in_column_headers(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "class_headers.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=True)
    ws = wb["Crew gear"]
    assert ws.cell(1, _FIRST_CHAR_COL).value == "Deflub ( PAL )"


def test_character_without_spell_file_has_plain_name(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Stablub_bristle-Inventory.txt"]
    report = build_crew_report(paths)
    out = tmp_path / "no_class.xlsx"
    write_crew_workbook(report, out)

    wb = load_workbook(out, data_only=True)
    ws = wb["Crew gear"]
    assert ws.cell(1, _FIRST_CHAR_COL).value == "Stablub"


def test_no_spell_tabs_without_data(tmp_path: Path) -> None:
    paths = [EXAMPLES / "Deflub_bristle-Inventory.txt"]
    out = tmp_path / "gear_only.xlsx"
    write_crew_workbook(build_crew_report(paths), out, spell_report=None)
    names = load_workbook(out).sheetnames
    assert "Missing Runes" not in names
    assert "Spell List" not in names
