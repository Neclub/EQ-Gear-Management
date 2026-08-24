from pathlib import Path
import json

from dataclasses import replace

from inventory_parser.achievement_parser import EVERQUEST_BASE_LABEL
from inventory_parser.achievement_report import build_achievement_report
from inventory_parser.cli import generate_workbook
from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.excel_export import MISSING_SPELLS_SHEET_NAME, MISSING_USEFUL_SPELLS_SHEET_NAME
from inventory_parser.html_export import extract_report_json, write_team_html
from inventory_parser.output_paths import html_path_for_workbook

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
SPELL_DATA = EXAMPLES / "SpellData"
ACHIEVEMENTS = EXAMPLES / "Achievements"
SHAMLUB_ACH = ACHIEVEMENTS / "Shamlub_xegony-Achievements.txt"


def test_html_path_for_workbook() -> None:
    xlsx = Path("D:/out/Bristlebane_Team Inventory.xlsx")
    assert html_path_for_workbook(xlsx) == Path("D:/out/Bristlebane_Team_Inventory.html")


def test_write_team_html_structure(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    spell = SPELL_DATA / "Deflub_bristle-PAL-MissingSpells.txt"
    bundle = build_export_bundle([inv, spell], include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)

    text = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in text
    assert "Team Inventory Report" in text
    assert "const REPORT =" in text
    assert 'id="sidebar"' in text
    assert 'id="navList"' in text
    assert 'id="characterFilter"' in text
    assert 'id="tierLegend"' in text
    assert "function paintTitleGraphic" in text
    assert "--gold:" in text
    assert "chip.dataset.key = character.name" in text
    assert "function filterChipLabel" in text
    assert "function rowMatchesCharacterFilter" in text
    assert "function sortedColumnIndices" in text
    assert "function cellText" in text
    assert "cell-chip" in text
    assert "Most missing" in text
    assert "Roster order" in text
    assert ">Visibility<" not in text
    for symbol_id in (
        "icon-shield",
        "icon-chart",
        "icon-rune",
        "icon-rune-stack",
        "icon-book",
        "icon-anvil",
        "icon-chest",
        "icon-trophy",
        "icon-gem",
        "icon-armor",
    ):
        assert f'id="{symbol_id}"' in text

    report = extract_report_json(text)
    assert report["meta"]["version"]
    assert report["meta"]["reportTitle"]
    assert report["meta"]["characterCount"] >= 1
    assert report["meta"]["characters"]
    assert report["meta"]["logoDataUri"].startswith("data:image/png;base64,")
    assert 'rel="icon"' in text
    assert report["meta"]["logoDataUri"] in text
    assert "favicon.href = meta.logoDataUri" in text
    titles = [section["title"] for section in report["sections"]]
    assert "Team Gear" in titles
    assert "Gear T-Level" in titles
    assert "Missing Runes" in titles
    assert MISSING_SPELLS_SHEET_NAME in titles
    assert MISSING_USEFUL_SPELLS_SHEET_NAME in titles
    assert report["meta"]["characters"][0]["classAbbr"]
    missing_runes = next(s for s in report["sections"] if s["id"] == "missing_runes")
    assert missing_runes["data"]["classAbbrs"]
    assert missing_runes["data"]["expansionOptions"]


def test_html_rune_inventory_present(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    text = out.read_text(encoding="utf-8")
    assert "Expansion" in text
    report = extract_report_json(text)
    section = next(s for s in report["sections"] if s["id"] == "rune_inventory")
    assert section["type"] == "rune_inventory"
    assert section["title"] == "Rune Inventory"
    assert section["data"]["expansionOptions"]
    assert "ToB" in section["data"]["expansionOptions"]
    tob = next(f for f in section["data"]["families"] if f["label"] == "ToB")
    deflub_idx = section["data"]["characters"].index("Deflub ( PAL )")
    minor_row = next(r for r in tob["rows"] if r["tier"] == "Minor")
    assert minor_row["counts"][deflub_idx] == 1


def test_html_rune_inventory_omitted_without_runes(tmp_path: Path) -> None:
    inv = EXAMPLES / "Stablub_bristle-Inventory.txt"
    bundle = build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    assert not any(section["id"] == "rune_inventory" for section in report["sections"])


def test_html_includes_item_link(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    text = out.read_text(encoding="utf-8")
    assert "items.eqresource.com/items.php?id=173940" in text


def test_html_gear_t_level_item_link_and_name(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    section = next(s for s in report["sections"] if s["id"] == "gear_t_level")
    charm = next(row for row in section["data"]["rows"] if row["slot"] == "Charm")
    cell = charm["cells"][0]
    assert cell["label"] == "TOB-R2"
    assert cell["name"] == "Defender's Charm of Rebellion"
    assert cell["url"] == "https://items.eqresource.com/items.php?id=173940"


def test_html_achievement_expansion_labels(tmp_path: Path) -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    bundle = build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False)
    ach_report = build_achievement_report(
        bundle.team,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    assert ach_report is not None
    bundle = replace(bundle, achievement_report=ach_report)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    assert report["meta"]["currentExpansion"] == "Shattering of Ro (2025)"
    assert "Rain of Fear (2012)" in report["expansionOrder"]
    assert EVERQUEST_BASE_LABEL in report["expansionOrder"]
    raid = next(s for s in report["sections"] if s["title"] == "Raid Achievements")
    expansions = {row[1] for row in raid["data"]["rows"]}
    assert any("Rain of Fear (2012)" in value for value in expansions)
    assert raid["data"]["columns"] == ["Character", "Expansion", "Raid", "Event", "Objective", "Status"]
    assert raid["data"]["eventColumn"] == 3
    assert raid["data"]["group"]["descriptionKind"] == "raids"
    assert any(
        row[2] == "Conqueror of Vulak`Aerr" and row[4] == "None Shall Pass"
        for row in raid["data"]["rows"]
    )
    assert any(row[3] == "Echo of Hate" for row in raid["data"]["rows"])
    quests = next(s for s in report["sections"] if s["id"] == "quests")
    data = quests["data"]
    assert data["characterColumn"] == 0
    assert data["expansionColumn"] == 1
    assert data["zoneColumn"] == 2
    assert data["columns"] == ["Character", "Expansion", "Zone", "Type", "Quest", "Status"]
    assert data["group"]["descriptionKind"] == "quests"
    assert any(
        row[2] == "Arcstone, Shattered Isles" and row[4] == "Quench the Fire"
        for row in data["rows"]
    )
    text = out.read_text(encoding="utf-8")
    assert "function updateAchievementGroupsContent" in text
    assert "quest-card" in text
    assert "Not Completed" in text


def test_html_unmade_gear_omitted_when_empty(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = replace(build_export_bundle([inv], include_spells=False, include_achievements=False, include_slot2=False), unmade_entries=[])
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    assert not any(section["title"] == "Unmade Gear" for section in report["sections"])


def test_html_spell_list_has_character_filter(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    spell = SPELL_DATA / "Deflub_bristle-PAL-MissingSpells.txt"
    bundle = build_export_bundle([inv, spell], include_achievements=False, include_slot2=False)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    text = out.read_text(encoding="utf-8")
    assert "All characters" in text
    assert "function refreshContent()" in text
    assert "ACHIEVEMENT_EXPANSION_TABS" in text
    assert "activeExpansionFilter" in text
    assert "expansionFilterOptions" in text
    assert "zoneFilterOptions" in text
    assert "eventFilterOptions" in text
    assert "Rune type" in text
    report = extract_report_json(text)
    spell_section = next(s for s in report["sections"] if s["id"] == "spell_list")
    data = spell_section["data"]
    assert data["characterColumn"] == 0
    assert data["runeColumn"] == 2
    assert data["expansionColumn"] == 3
    assert "blockColumn" not in data
    assert "blockOptions" not in data
    assert data["runeOptions"]
    assert data["rows"]
    assert any(row[3] for row in data["rows"])
    assert "cell-chip" in text


def test_cli_also_html_flag(tmp_path: Path) -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    xlsx = tmp_path / "crew.xlsx"
    saved, warnings, html_saved = generate_workbook(
        [inv],
        xlsx,
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        include_raid_bis=False,
        also_html=True,
    )
    assert saved == xlsx
    assert html_saved == html_path_for_workbook(xlsx)
    assert html_saved.is_file()
    assert not warnings or isinstance(warnings, list)


def test_embedded_json_row_counts_match_bundle(tmp_path: Path) -> None:
    inv = EXAMPLES / "Shamlub_bristle-Inventory.txt"
    spell = SPELL_DATA / "Shamlub_bristle-SHM-MissingSpells.txt"
    bundle = build_export_bundle([inv, spell], include_achievements=False, include_slot2=False)
    ach_report = build_achievement_report(
        bundle.team,
        achievement_paths={"shamlub_bristle": SHAMLUB_ACH},
    )
    if ach_report is not None:
        bundle = replace(bundle, achievement_report=ach_report)
    out = tmp_path / "crew.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))

    if bundle.spell_report is not None:
        spell_section = next(s for s in report["sections"] if s["title"] == MISSING_SPELLS_SHEET_NAME)
        assert len(spell_section["data"]["rows"]) == len(bundle.spell_report.entries)

    if bundle.achievement_report and bundle.achievement_report.missing_collections:
        missing = next(s for s in report["sections"] if s["title"] == "Missing Collections")
        assert len(missing["data"]["rows"]) == len(bundle.achievement_report.missing_collections)
        assert missing["data"]["copyColumn"] == 4
        assert "function copyTextToClipboard" in out.read_text(encoding="utf-8")
        assert "function showCopyBalloon" in out.read_text(encoding="utf-8")
        assert "Copied to clipboard" in out.read_text(encoding="utf-8")
        assert "copy-col-head" in out.read_text(encoding="utf-8")
        assert "Clicking the link copies the name to your clipboard." in out.read_text(encoding="utf-8")


def test_json_for_html_script_blocks_script_breakout() -> None:
    from inventory_parser.html_export import escape_json_for_script, json_for_html_script

    payload = json_for_html_script({"name": "</script><script>alert(1)</script>"})
    assert "</script>" not in payload
    assert "\\u003c" in payload
    restored = json.loads(payload)
    assert restored["name"] == "</script><script>alert(1)</script>"
    already = json.dumps({"x": "</script>"}, ensure_ascii=False)
    assert "</script>" not in escape_json_for_script(already)


def test_html_report_escapes_script_breakout_in_item_name(tmp_path: Path) -> None:
    from inventory_parser.html_export import extract_report_json, write_team_html

    inv = tmp_path / "Xsslub_bristle-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Chest\t</script><script>alert(1)</script>\t168096\t1\t5\n",
        encoding="utf-8",
    )
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        include_raid_bis=False,
        fetch_chest_class=False,
        fetch_eqr_gear_tiers=False,
    )
    out = tmp_path / "xss.html"
    write_team_html(bundle, out)
    text = out.read_text(encoding="utf-8")
    script_json = text.split("const REPORT = ", 1)[1].split(";\n", 1)[0]
    assert "</script>" not in script_json
    report = extract_report_json(text)
    names = [
        cell.get("name")
        for section in report["sections"]
        if section.get("type") == "gear_matrix"
        for row in section["data"]["rows"]
        for cell in row["cells"]
        if cell
    ]
    assert "</script><script>alert(1)</script>" in names


def test_html_not_purchased_spell_chip(tmp_path: Path) -> None:
    inv = tmp_path / "Zenbane_bristle-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\nChest\tCloth Shirt\t1001\t1\t5\n",
        encoding="utf-8",
    )
    spell = tmp_path / "Zenbane_bristle-CLR-MissingSpells.txt"
    spell.write_text(
        "126\tAppeasement\n126\tAwestruck XVII\n126\tWord of Wellbeing Rk. II\n",
        encoding="utf-8",
    )
    bundle = build_export_bundle(
        [inv, spell],
        include_achievements=False,
        include_slot2=False,
        include_raid_bis=False,
        fetch_chest_class=False,
        fetch_eqr_gear_tiers=False,
    )
    out = tmp_path / "zenbane.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    spell_section = next(s for s in report["sections"] if s["id"] == "spell_list")
    by_spell = {row[4]["text"] if isinstance(row[4], dict) else row[4]: row[4] for row in spell_section["data"]["rows"]}
    assert by_spell["Appeasement Rk. III"] == {
        "text": "Appeasement Rk. III",
        "chip": "Not Purchased",
    }
    assert by_spell["Awestruck XVII Rk. III"]["chip"] == "Not Purchased"
    assert by_spell["Word of Wellbeing Rk. III"] == "Word of Wellbeing Rk. III"
