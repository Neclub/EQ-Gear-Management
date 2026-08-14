"""Tests for Chest-armor class detection."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.slot2_augs.chest_class import (
    detect_class_from_chest,
    equipped_chest_item,
    parse_class_list,
    parse_eqresource_item_classes,
    parse_raidloot_item_classes,
    profile_from_class,
    resolve_classes_for_inventories,
)
from inventory_parser.parser import InventoryData, InventoryItem

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_class_list_aliases():
    assert parse_class_list("ROG") == ["ROG"]
    assert parse_class_list("Rogue") == ["ROG"]
    assert parse_class_list("Shadow Knight") == ["SHD"]
    assert parse_class_list("WAR PAL SHD") == ["WAR", "PAL", "SHD"]
    assert parse_class_list("All") == []


def test_parse_raidloot_chest_rog():
    html = (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8")
    assert parse_raidloot_item_classes(html) == ["ROG"]


def test_parse_eqresource_chest_monk():
    html = (FIXTURES / "eqresource_chest_173849_mnk.html").read_text(encoding="utf-8")
    assert parse_eqresource_item_classes(html) == ["MNK"]


def test_detect_class_from_chest_override():
    data = InventoryData(
        character="Stablub",
        server="bristle",
        filepath="Stablub_bristle-Inventory.txt",
        items=[InventoryItem("Chest", "Rogue Chest", 175863, 1, 6)],
    )
    chest = equipped_chest_item(data)
    assert chest is not None
    assert chest.item_id == 175863
    rl = (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8")
    assert (
        detect_class_from_chest(
            data,
            overrides={175863: (rl, None)},
            allow_network=False,
        )
        == "ROG"
    )


def test_profile_from_detected_classes():
    assert profile_from_class("ROG") == "dex"
    assert profile_from_class("WIZ") == "int"
    assert profile_from_class("CLR") == "wis"
    assert profile_from_class(None) == "dex"


def test_resolve_classes_from_chest_override():
    stablub = InventoryData(
        character="Stablub",
        server="bristle",
        filepath="Stablub_bristle-Inventory.txt",
        items=[InventoryItem("Chest", "Rogue Chest", 175863, 1, 6)],
    )
    overrides = {
        175863: (
            (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8"),
            None,
        ),
    }
    by_path = resolve_classes_for_inventories(
        [stablub],
        overrides=overrides,
        allow_network=False,
    )
    assert by_path[str(Path(stablub.filepath))] == "ROG"
    data = InventoryData(
        character="Forceclass",
        server="test",
        filepath="Forceclass_test-WAR-Inventory.txt",
        class_abbr="WAR",
        items=[
            InventoryItem("Chest", "Some Tunic", 175863, 1, 6),
        ],
    )
    rl = (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8")
    by_path = resolve_classes_for_inventories(
        [data],
        overrides={175863: (rl, None)},
        allow_network=False,
    )
    assert by_path[str(Path(data.filepath))] == "WAR"
