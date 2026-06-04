from pathlib import Path

from inventory_parser.parser import (
    extract_equipped_items,
    parse_character_from_filename,
    parse_inventory_filename,
    parse_inventory_file,
)
from inventory_parser.slots import CREW_GEAR_SLOTS

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"


def test_parse_character_from_filename() -> None:
    assert parse_character_from_filename("Deflub_bristle-Inventory.txt") == ("Deflub", "bristle")


def test_parse_inventory_filename() -> None:
    assert parse_inventory_filename("Deflub_bristle-Inventory.txt") == (
        "Deflub",
        "bristle",
    )


def test_extract_equipped_deflub_arms() -> None:
    data = parse_inventory_file(EXAMPLES / "Deflub_bristle-Inventory.txt")
    assert data is not None
    equipped, evolver_keys = extract_equipped_items(data)
    assert equipped["Arms"].name == "Exarch Vambraces of Eternal Reverie"
    assert equipped["Ear-1"].name == "Adroit Earring of Eternal Reverie"
    assert equipped["Ear-2"].name == "Blooded Righteous Protector's Earring of Rallos"
    assert "Ear-2" in evolver_keys
    assert "Ear-1" not in evolver_keys


def test_crew_slots_subset_of_output_slots() -> None:
    data = parse_inventory_file(EXAMPLES / "Monklub_bristle-Inventory.txt")
    assert data is not None
    equipped, _evolver_keys = extract_equipped_items(data)
    for slot in CREW_GEAR_SLOTS:
        if slot in equipped:
            assert equipped[slot].name != "Empty"
