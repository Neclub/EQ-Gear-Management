"""Tests for Chest-armor class detection."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.slot2_augs.chest_class import (
    choose_class_abbr,
    detect_class_from_chest,
    equipped_chest_item,
    parse_class_list,
    parse_eqresource_item_classes,
    parse_raidloot_item_classes,
    profile_from_class,
    resolve_character_class,
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
    assert by_path[str(Path(data.filepath))] == "ROG"


def test_choose_class_abbr_prefers_single_chest_class() -> None:
    assert choose_class_abbr(["ROG"], "WAR") == "ROG"
    assert choose_class_abbr([], "WAR") == "WAR"
    assert choose_class_abbr(["WAR", "PAL", "SHD"], "PAL") == "PAL"
    assert choose_class_abbr(["WAR", "PAL"], None) == "WAR"


def test_filename_fallback_when_no_chest() -> None:
    data = InventoryData(
        character="Forceclass",
        server="test",
        filepath="Forceclass_test-WAR-Inventory.txt",
        class_abbr="WAR",
        items=[],
    )
    by_path = resolve_classes_for_inventories([data], allow_network=False)
    assert by_path[str(Path(data.filepath))] == "WAR"


def test_resolve_character_class_chest_overrides_filename() -> None:
    data = InventoryData(
        character="Forceclass",
        server="test",
        filepath="Forceclass_test-WAR-Inventory.txt",
        class_abbr="WAR",
        items=[InventoryItem("Chest", "Rogue Chest", 175863, 1, 6)],
    )
    rl = (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8")
    assert (
        resolve_character_class(
            data,
            explicit_class="WAR",
            overrides={175863: (rl, None)},
            allow_network=False,
        )
        == "ROG"
    )


def test_export_bundle_uses_worn_chest_over_filename(tmp_path: Path) -> None:
    inv = tmp_path / "Forceclass_test-WAR-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Chest\tRogue Chest\t175863\t1\t6\n",
        encoding="utf-8",
    )
    rl = (FIXTURES / "raidloot_chest_175863_rog.html").read_text(encoding="utf-8")
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        chest_class_overrides={175863: (rl, None)},
        fetch_chest_class=False,
    )
    assert bundle.team.characters[0].class_abbr == "ROG"
    assert bundle.team.characters[0].display_name == "Forceclass ( ROG )"
