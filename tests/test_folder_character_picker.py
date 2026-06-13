from pathlib import Path

from inventory_parser.team_report import discover_folder_character_choices

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"


def test_discover_folder_character_choices_from_examples() -> None:
    choices = discover_folder_character_choices(EXAMPLES)
    names = {c.display_name for c in choices}
    assert "Deflub ( PAL )" in names
    assert "Stablub" in names
    assert len(choices) == 7


def test_spelldata_files_grouped_with_inventory() -> None:
    choices = discover_folder_character_choices(EXAMPLES)
    deflub = next(c for c in choices if c.character == "Deflub")
    assert len(deflub.inventory_paths) == 1
    assert deflub.inventory_paths[0].name == "Deflub_bristle-Inventory.txt"
    assert len(deflub.spell_paths) == 1
    assert deflub.spell_paths[0].name == "Deflub_bristle-PAL-MissingSpells.txt"
    assert deflub.summary == "bristle · 1 inventory · 1 MissingSpells"


def test_stablub_inventory_only() -> None:
    choices = discover_folder_character_choices(EXAMPLES)
    stablub = next(c for c in choices if c.character == "Stablub")
    assert stablub.inventory_paths
    assert stablub.spell_paths == ()


def test_discover_folder_character_choices_spelldata_only(tmp_path: Path) -> None:
    spell = tmp_path / "SpellData"
    spell.mkdir()
    spell_file = spell / "Orphan_bristle-WIZ-MissingSpells.txt"
    spell_file.write_text("126\tExample Rk. III\n", encoding="utf-8")
    choices = discover_folder_character_choices(tmp_path)
    assert len(choices) == 1
    assert choices[0].display_name == "Orphan ( WIZ )"
    assert choices[0].inventory_paths == ()
    assert len(choices[0].spell_paths) == 1
