from pathlib import Path

from inventory_parser.team_report import (
    CharacterGear,
    TeamGearReport,
    build_team_report,
    format_character_display_name,
)
from inventory_parser.missing_spells import (
    counts_as_missing_rk3,
    discover_missing_spells_for_inventories,
    discover_persona_bindings,
    is_inventory_file,
    is_missing_rank_ii,
    is_missing_rank_iii,
    is_missing_spells_file,
    normalize_spell_rank_iii,
    parse_missing_spells_file,
    parse_missing_spells_filename,
    persona_key,
    split_input_paths,
    strip_spell_rank,
)
from inventory_parser.spell_report import build_spell_rune_report

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
SPELL_DATA = EXAMPLES / "SpellData"

SPELL_FILES = {
    "Deflub": SPELL_DATA / "Deflub_bristle-PAL-MissingSpells.txt",
    "Monklub": SPELL_DATA / "Monklub_bristle-MNK-MissingSpells.txt",
    "Healub": SPELL_DATA / "Healub_bristle-CLR-MissingSpells.txt",
    "Kawiika": SPELL_DATA / "Rk II" / "Kawiika_bristle-WIZ-MissingSpells.txt",
}


def test_input_path_classification() -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    spell = SPELL_FILES["Deflub"]
    ach = EXAMPLES / "Achievements" / "Shamlub_xegony-Achievements.txt"
    inventory_paths, spell_paths, achievement_paths = split_input_paths([inv, spell, ach])
    assert is_inventory_file(inv)
    assert is_missing_spells_file(spell)
    assert inventory_paths == [inv]
    assert spell_paths == [spell]
    assert achievement_paths == [ach]


def test_explicit_spell_file_without_spelldata_folder() -> None:
    inv = EXAMPLES / "Monklub_bristle-Inventory.txt"
    spell = SPELL_FILES["Monklub"]
    discovery = discover_missing_spells_for_inventories([], extra_spell_paths=[spell])
    assert discovery.paths[persona_key("Monklub", "bristle", "MNK")] == spell.resolve()
    report = build_spell_rune_report(
        build_team_report([inv], spell_paths=[spell]),
        inventory_paths=[inv],
        extra_spell_paths=[spell],
    )
    assert report is not None
    assert any(e.character == "Monklub" for e in report.entries)


def test_format_character_display_name() -> None:
    assert format_character_display_name("Deflub", "PAL") == "Deflub ( PAL )"
    assert format_character_display_name("Stablub", None) == "Stablub"


def test_class_from_spelldata_via_bindings() -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    report = build_team_report([inv])
    assert report.characters[0].class_abbr == "PAL"
    assert report.characters[0].display_name == "Deflub ( PAL )"


def test_filename_parse() -> None:
    assert parse_missing_spells_filename(SPELL_FILES["Deflub"]) == (
        "Deflub",
        "bristle",
        "PAL",
    )


def test_rank_iii_detection() -> None:
    assert is_missing_rank_iii("Committal Rk. III") is True
    assert is_missing_rank_iii("Phantom Silhouette Rk. II") is False
    assert is_missing_rank_iii("Aurora of Sunlight XI") is False


def test_rank_ii_detection_and_normalization() -> None:
    assert is_missing_rank_ii("Concussive Blast XII Rk. II") is True
    assert is_missing_rank_ii("Committal Rk. III") is False
    assert counts_as_missing_rk3("Concussive Blast XII Rk. II") is True
    assert counts_as_missing_rk3("Committal Rk. III") is True
    assert counts_as_missing_rk3("Aurora of Sunlight XI") is False
    assert strip_spell_rank("Concussive Blast XII Rk. II") == "Concussive Blast XII"
    assert normalize_spell_rank_iii("Concussive Blast XII Rk. II") == (
        "Concussive Blast XII Rk. III"
    )
    assert normalize_spell_rank_iii("Committal Rk. III") == "Committal Rk. III"


def test_discover_spell_files_from_examples() -> None:
    inventories = sorted(EXAMPLES.glob("*-Inventory.txt"))
    discovery = discover_missing_spells_for_inventories(inventories)
    assert len(discovery.paths) == 6
    assert discovery.paths[persona_key("Deflub", "bristle", "PAL")] == SPELL_FILES["Deflub"].resolve()


def test_monklub_rk3_entries() -> None:
    lines = parse_missing_spells_file(SPELL_FILES["Monklub"])
    rk3 = [ln for ln in lines if is_missing_rank_iii(ln.name) and ln.level >= 121]
    names = {ln.name for ln in rk3}
    assert "Storied Reflexes Rk. III" in names
    assert "Phantom Silhouette Rk. II" not in names


def test_deflub_126_130_rune_counts() -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    report = build_spell_rune_report(
        build_team_report([inv]),
        inventory_paths=[inv],
    )
    assert report is not None
    counts = report.counts_by_persona[persona_key("Deflub", "bristle", "PAL")]["126-130"]
    assert counts["Minor"] == 7
    assert counts["Lesser"] == 7
    assert counts["Median"] == 5
    assert counts["Greater"] == 5
    assert counts["Glowing"] == 5


def test_spell_report_entries_have_rune() -> None:
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    report = build_spell_rune_report(build_team_report([inv]), inventory_paths=[inv])
    assert report is not None
    sample = next(e for e in report.entries if e.spell_name == "Committal Rk. III")
    assert sample.level == 126
    assert sample.rune_tier == "Minor"
    assert sample.block_label == "126-130"


def test_kawiika_rk2_counts_as_rk3_at_126_130() -> None:
    pk = persona_key("Kawiika", "bristle", "WIZ")
    team = TeamGearReport(
        spell_characters=[
            CharacterGear(
                character="Kawiika",
                server="bristle",
                filepath="",
                class_abbr="WIZ",
            )
        ]
    )
    report = build_spell_rune_report(
        team,
        spell_paths={pk: SPELL_FILES["Kawiika"]},
    )
    assert report is not None
    counts = report.counts_by_persona[pk]["126-130"]
    assert counts["Minor"] == 7
    assert counts["Lesser"] == 7
    assert counts["Median"] == 6
    assert counts["Greater"] == 6
    assert counts["Glowing"] == 5
    sample = next(
        e for e in report.entries if e.spell_name == "Concussive Blast XII Rk. III"
    )
    assert sample.level == 126
    assert sample.rune_tier == "Minor"
    low_level_rk2 = [
        e
        for e in report.entries
        if e.level < 121 and "Rk. III" in e.spell_name
    ]
    assert low_level_rk2 == []


def test_dedupe_rk2_and_rk3_same_level(tmp_path: Path) -> None:
    spell_file = tmp_path / "Dedupe_bristle-WIZ-MissingSpells.txt"
    spell_file.write_text(
        "126\tExample Spell Rk. II\n126\tExample Spell Rk. III\n",
        encoding="utf-8",
    )
    pk = persona_key("Dedupe", "bristle", "WIZ")
    team = TeamGearReport(
        spell_characters=[
            CharacterGear(
                character="Dedupe",
                server="bristle",
                filepath="",
                class_abbr="WIZ",
            )
        ]
    )
    report = build_spell_rune_report(team, spell_paths={pk: spell_file})
    assert report is not None
    matches = [e for e in report.entries if e.level == 126]
    assert len(matches) == 1
    assert matches[0].spell_name == "Example Spell Rk. III"
