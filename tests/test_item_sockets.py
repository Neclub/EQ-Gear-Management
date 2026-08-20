"""Tests for parent-item type 7/8 socket map lookup."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.slot2_augs.item_sockets import (
    fetch_item_sockets,
    parse_eqresource_item_html,
    parse_raidloot_item_html,
    resolve_type5_slots,
    resolve_type78_slots,
    type5_dump_slot,
    type78_dump_slot,
)
from inventory_parser.parser import (
    InventoryData,
    InventoryItem,
    collect_equipped_parent_ids,
    extract_slot2_augs,
    extract_type5_augs,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_raidloot_head_slot2_type8():
    html = (FIXTURES / "raidloot_item_175860.html").read_text(encoding="utf-8")
    sockets = parse_raidloot_item_html(html, 175860)
    assert type78_dump_slot(sockets) == 2
    assert type5_dump_slot(sockets) == 1
    assert [(s.slot, s.aug_type) for s in sockets] == [(1, 5), (2, 8), (3, 14)]


def test_parse_raidloot_ear_slot3_type8():
    html = (FIXTURES / "raidloot_item_175914.html").read_text(encoding="utf-8")
    sockets = parse_raidloot_item_html(html, 175914)
    assert type78_dump_slot(sockets) == 3
    assert type5_dump_slot(sockets) == 2


def test_parse_raidloot_face_evolver_slot4():
    html = (FIXTURES / "raidloot_item_168096.html").read_text(encoding="utf-8")
    sockets = parse_raidloot_item_html(html, 168096)
    assert type78_dump_slot(sockets) == 4
    assert type5_dump_slot(sockets) == 3


def test_parse_eqresource_fallback_face():
    html = (FIXTURES / "eqresource_item_168096.html").read_text(encoding="utf-8")
    sockets = parse_eqresource_item_html(html)
    assert type78_dump_slot(sockets) == 4
    assert type5_dump_slot(sockets) == 3
    assert any(s.slot == 6 and s.aug_type == 19 for s in sockets)


def test_type78_picks_first_of_7_and_8():
    html = (
        '<label>Slot 1, type 3:</label>'
        '<label>Slot 2, type 7:</label>'
        '<label>Slot 3, type 8:</label>'
    )
    sockets = parse_raidloot_item_html(html)
    assert type78_dump_slot(sockets) == 2


def test_fetch_override_raidloot_then_eqr():
    raid = (FIXTURES / "raidloot_item_168096.html").read_text(encoding="utf-8")
    sock = fetch_item_sockets(168096, html_override=raid)
    assert type78_dump_slot(sock.sockets) == 4
    assert sock.source == "raidloot"

    eqr = (FIXTURES / "eqresource_item_168096.html").read_text(encoding="utf-8")
    sock2 = fetch_item_sockets(168096, html_override="<html></html>", eqr_html_override=eqr)
    assert type78_dump_slot(sock2.sockets) == 4
    assert sock2.source == "eqresource"


def test_resolve_type78_slots_with_overrides():
    overrides = {
        175860: ((FIXTURES / "raidloot_item_175860.html").read_text(encoding="utf-8"), None),
        175914: ((FIXTURES / "raidloot_item_175914.html").read_text(encoding="utf-8"), None),
        168096: ((FIXTURES / "raidloot_item_168096.html").read_text(encoding="utf-8"), None),
    }
    resolved = resolve_type78_slots([175860, 175914, 168096], overrides=overrides)
    assert resolved[175860] == 2
    assert resolved[175914] == 3
    assert resolved[168096] == 4


def test_resolve_type5_slots_with_overrides():
    overrides = {
        175860: ((FIXTURES / "raidloot_item_175860.html").read_text(encoding="utf-8"), None),
        175914: ((FIXTURES / "raidloot_item_175914.html").read_text(encoding="utf-8"), None),
        168096: ((FIXTURES / "raidloot_item_168096.html").read_text(encoding="utf-8"), None),
    }
    resolved = resolve_type5_slots([175860, 175914, 168096], overrides=overrides)
    assert resolved[175860] == 1
    assert resolved[175914] == 2
    assert resolved[168096] == 3


def test_extract_type5_equipped_empty_and_missing():
    """Equipped name, Empty dump row, and missing dump row all use the socket map."""
    data = InventoryData(
        character="Test",
        server="s",
        filepath="x",
        items=[
            InventoryItem("Head", "Helm of Tests", 175860, 1, 3),
            InventoryItem("Head-Slot1", "Immovable Green Gem", 173378, 1, 0),
            InventoryItem("Head-Slot2", "Some Type78", 999, 1, 0),
            InventoryItem("Ear", "Earring A", 175914, 1, 4),
            InventoryItem("Ear-Slot2", "Empty", 0, 0, 0),
            InventoryItem("Face", "Yearning Restored Mask of the Vortex", 168096, 1, 6),
            # no Face-Slot3 row → should fill Empty
        ],
    )
    rows = {
        r.gear_slot: r
        for r in extract_type5_augs(
            data, type5_slot_by_parent_id={175860: 1, 175914: 2, 168096: 3}
        )
    }
    assert set(rows) == {"Head", "Ear-1", "Face"}
    assert rows["Head"].name == "Immovable Green Gem"
    assert rows["Head"].item_id == 173378
    assert rows["Head"].dump_slot == 1
    assert rows["Ear-1"].name is None
    assert rows["Ear-1"].item_id is None
    assert rows["Ear-1"].dump_slot == 2
    assert rows["Face"].name is None
    assert rows["Face"].dump_slot == 3


def test_extract_type5_skips_parents_without_map():
    data = InventoryData(
        character="Test",
        server="s",
        filepath="x",
        items=[
            InventoryItem("Head", "Helm", 100, 1, 3),
            InventoryItem("Head-Slot2", "Something", 1, 1, 0),
        ],
    )
    assert extract_type5_augs(data, type5_slot_by_parent_id={}) == []


def test_extract_face_evolver_uses_slot4_map():
    data = InventoryData(
        character="Shieldlub",
        server="test",
        filepath="x",
        items=[
            InventoryItem("Face", "Yearning Restored Mask of the Vortex", 168096, 1, 6),
            InventoryItem("Face-Slot2", "Empty", 0, 0, 0),
            InventoryItem("Face-Slot3", "Empty", 0, 0, 0),
            InventoryItem("Face-Slot4", "Protector's Gem of Uprising", 173574, 1, 6),
        ],
    )
    without = {s.gear_slot: s for s in extract_slot2_augs(data)}
    assert without["Face"].name is None  # heuristic Slot2 empty
    assert without["Face"].dump_slot == 2

    with_map = {
        s.gear_slot: s
        for s in extract_slot2_augs(data, type78_slot_by_parent_id={168096: 4})
    }
    assert with_map["Face"].name == "Protector's Gem of Uprising"
    assert with_map["Face"].dump_slot == 4
    assert with_map["Face"].parent_id == 168096
    assert with_map["Face"].socket_map_hit is True


def test_collect_parent_ids_skips_primary_and_weapon_secondary():
    data = InventoryData(
        character="X",
        server="s",
        filepath="x",
        items=[
            InventoryItem("Head", "Helm", 100, 1, 6),
            InventoryItem("Primary", "Sword", 200, 1, 6),
            InventoryItem("Secondary", "Spear", 300, 1, 6),
        ],
    )
    ids = collect_equipped_parent_ids(data)
    assert ids == [100]

    shield = InventoryData(
        character="X",
        server="s",
        filepath="x",
        items=[
            InventoryItem("Secondary", "Tower Shield of Rebellion", 173941, 1, 6),
        ],
    )
    assert collect_equipped_parent_ids(shield) == [173941]