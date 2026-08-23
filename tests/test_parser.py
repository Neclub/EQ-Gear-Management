from pathlib import Path

from inventory_parser.parser import (
    InventoryData,
    InventoryItem,
    collect_equipped_aug_locations,
    collect_owned_item_ids,
    extract_equipped_items,
    extract_slot2_augs,
    parent_name_is_shield,
    parse_character_from_filename,
    parse_inventory_filename,
    parse_inventory_file,
)
from inventory_parser.slots import TEAM_GEAR_SLOTS

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"


def test_parse_character_from_filename() -> None:
    assert parse_character_from_filename("Deflub_bristle-Inventory.txt") == ("Deflub", "bristle")


def test_parse_inventory_filename() -> None:
    assert parse_inventory_filename("Deflub_bristle-Inventory.txt") == (
        "Deflub",
        "bristle",
        None,
    )


def test_parse_inventory_filename_with_class() -> None:
    assert parse_inventory_filename("Deflub_bristle-PAL-Inventory.txt") == (
        "Deflub",
        "bristle",
        "PAL",
    )
    assert parse_inventory_filename("Deflub_bristle-WAR-Inventory.txt") == (
        "Deflub",
        "bristle",
        "WAR",
    )
    assert parse_character_from_filename("Deflub_bristle-SHD-Inventory.txt") == (
        "Deflub",
        "bristle",
    )


def test_collect_equipped_aug_locations() -> None:
    data = InventoryData(
        character="Test",
        server="bristle",
        filepath="test.txt",
        items=[
            InventoryItem("Chest", "Some Chest", 1, 1, 6),
            InventoryItem("Chest-Slot3", "Ornate Attacker of the Harbinger", 169780, 1, 0),
            InventoryItem("Ear", "Left Ear", 2, 1, 6),
            InventoryItem("Ear-Slot1", "Aug In Ear One", 100, 1, 0),
            InventoryItem("Ear", "Right Ear", 3, 1, 6),
            InventoryItem("Ear-Slot1", "Aug In Ear Two", 101, 1, 0),
            InventoryItem("General 1-Slot1", "Ornate Attacker of the Harbinger", 169780, 1, 0),
        ],
    )
    by_id, by_name = collect_equipped_aug_locations(data)
    assert by_id[169780] == "Chest"
    assert by_id[100] == "Ear-1"
    assert by_id[101] == "Ear-2"
    assert by_name["ornate attacker of the harbinger"] == "Chest"
    # Bag copy does not override or append as a bag location.
    assert "General" not in by_id[169780]


def test_parse_inventory_file_stores_class_abbr() -> None:
    special = EXAMPLES / "SpecialNaming" / "Deflub_bristle-WAR-Inventory.txt"
    data = parse_inventory_file(special)
    assert data is not None
    assert data.character == "Deflub"
    assert data.server == "bristle"
    assert data.class_abbr == "WAR"


def test_extract_equipped_deflub_arms() -> None:
    data = parse_inventory_file(EXAMPLES / "Deflub_bristle-Inventory.txt")
    assert data is not None
    equipped, evolver_keys = extract_equipped_items(data)
    assert equipped["Arms"].name == "Exarch Vambraces of Eternal Reverie"
    assert equipped["Ear-1"].name == "Adroit Earring of Eternal Reverie"
    assert equipped["Ear-2"].name == "Blooded Righteous Protector's Earring of Rallos"
    assert "Ear-2" in evolver_keys
    assert "Ear-1" not in evolver_keys


def test_team_slots_subset_of_output_slots() -> None:
    data = parse_inventory_file(EXAMPLES / "Monklub_bristle-Inventory.txt")
    assert data is not None
    equipped, _evolver_keys = extract_equipped_items(data)
    for slot in TEAM_GEAR_SLOTS:
        if slot in equipped:
            assert equipped[slot].name != "Empty"


def test_extract_equipped_items_skips_slot_rows() -> None:
    data = parse_inventory_file(EXAMPLES / "Deflub_bristle-Inventory.txt")
    assert data is not None
    equipped, _evolver_keys = extract_equipped_items(data)
    for item in equipped.values():
        assert "-Slot" not in item.location


def test_extract_slot2_augs_from_deflub() -> None:
    data = parse_inventory_file(EXAMPLES / "Deflub_bristle-Inventory.txt")
    assert data is not None
    slot2 = {s.gear_slot: s for s in extract_slot2_augs(data)}
    assert not any(s.gear_slot.startswith("General") for s in slot2.values())
    if "Ear-1" in slot2:
        assert slot2["Ear-1"].dump_slot >= 2


def test_range_bow_detected_by_slots_and_name() -> None:
    from inventory_parser.parser import (
        is_range_bow,
        range_has_bow_slots,
        range_name_looks_like_bow,
        type78_dump_slot_for_parent,
        type78_dump_slot_for_range,
    )

    assert range_has_bow_slots({1, 2, 3, 4})
    assert range_has_bow_slots({1, 2, 3, 4, 5})
    assert not range_has_bow_slots({1, 2, 3})
    assert range_name_looks_like_bow("Short Bow of Rebellion")
    assert range_name_looks_like_bow("Ornate Crossbow")
    assert not range_name_looks_like_bow("Favor of the Chosen")
    assert is_range_bow(slot_numbers={1, 2, 3, 4}, item_name="Short Bow of Rebellion")
    assert not is_range_bow(slot_numbers={1, 2, 3}, item_name="Short Bow of Rebellion")
    assert not is_range_bow(slot_numbers={1, 2, 3, 4}, item_name="Favor of the Chosen")
    assert type78_dump_slot_for_range(is_bow=True) == 4
    assert type78_dump_slot_for_range(is_bow=False) == 2
    assert type78_dump_slot_for_parent("Range", range_is_bow=True) == 4
    assert type78_dump_slot_for_parent("Range", range_is_bow=False) == 2


def test_parent_name_is_shield() -> None:
    assert parent_name_is_shield("Tower Shield of Rebellion")
    assert parent_name_is_shield("Aegis of the Sea")
    assert not parent_name_is_shield("Short Spear of Resonant Fracture")
    assert not parent_name_is_shield("Empty")
    assert not parent_name_is_shield(None)
    assert not parent_name_is_shield("Windshield Wiper")


def test_collect_owned_item_ids_includes_bags_excludes_empty() -> None:
    data = InventoryData(
        character="Test",
        server="xegony",
        filepath="Test_xegony-Inventory.txt",
        items=[
            InventoryItem("Ear", "Earring", 100, 1, 6),
            InventoryItem("Ear-Slot2", "Equipped Aug", 200, 1, 0),
            InventoryItem("General 1-Slot3", "Bag Aug", 300, 1, 0),
            InventoryItem("Bank 1-Slot1", "Bank Aug", 400, 1, 0),
            InventoryItem("Charm-Slot2", "Empty", 0, 0, 0),
            InventoryItem("General 2-Slot1", "Empty", 0, 0, 0),
        ],
    )
    owned = collect_owned_item_ids(data)
    assert owned == {100, 200, 300, 400}
