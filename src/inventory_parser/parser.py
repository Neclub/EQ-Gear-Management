"""Parse EverQuest inventory dump text files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from inventory_parser.slots import EQUIPMENT_SLOT_BASES

_INVENTORY_FILENAME_RE = re.compile(
    r"^(.+)_([^-]+)-Inventory\.txt$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InventoryItem:
    location: str
    name: str
    item_id: int
    count: int
    augment_slots: int | None = None  # 5th column (max augment slots on item)


@dataclass
class InventoryData:
    character: str
    server: str
    filepath: str
    items: list[InventoryItem] = field(default_factory=list)


def parse_inventory_filename(filepath: str | Path) -> tuple[str, str]:
    """Extract character and server from ``{Char}_{Server}-Inventory.txt``."""
    name = Path(filepath).name
    match = _INVENTORY_FILENAME_RE.match(name)
    if match:
        return match.group(1), match.group(2)
    stem = Path(filepath).stem
    if stem.endswith("-Inventory"):
        stem = stem[: -len("-Inventory")]
    parts = stem.rsplit("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return stem, ""


def parse_character_from_filename(filepath: str | Path) -> tuple[str, str]:
    """Extract character and server from ``{Char}_{Server}-Inventory.txt``."""
    return parse_inventory_filename(filepath)


def parse_inventory_file(filepath: str | Path) -> InventoryData | None:
    """Parse a tab-separated inventory dump. Returns None if the file is missing."""
    path = Path(filepath)
    if not path.is_file():
        return None

    character, server = parse_inventory_filename(path)
    items: list[InventoryItem] = []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    for i, raw in enumerate(text.splitlines()):
        line = raw.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 3:
            continue

        if i == 0 and parts[0].lower() == "location" and parts[1].lower() == "name":
            continue

        location = parts[0].strip()
        name = parts[1].strip()
        try:
            item_id = int(parts[2].strip())
        except ValueError:
            continue

        if name == "Empty" and item_id == 0 and "-Slot" not in location:
            continue

        if len(parts) >= 4:
            try:
                count = int(parts[3].strip())
            except ValueError:
                count = 1
        else:
            count = 1

        augment_slots: int | None = None
        if len(parts) >= 5:
            try:
                augment_slots = int(parts[4].strip())
            except ValueError:
                augment_slots = None

        items.append(
            InventoryItem(
                location=location,
                name=name,
                item_id=item_id,
                count=count,
                augment_slots=augment_slots,
            )
        )

    return InventoryData(
        character=character,
        server=server,
        filepath=str(path.resolve()),
        items=items,
    )


def collect_item_names(data: InventoryData) -> list[str]:
    """Unique item names from an inventory dump, sorted alphabetically."""
    names = {item.name for item in data.items}
    return sorted(names, key=str.casefold)


def extract_equipped_items(
    data: InventoryData,
) -> tuple[dict[str, InventoryItem], set[str]]:
    """
    Map normalized crew slots (e.g. ``Ear-1``) to the equipped item in that slot.

    Returns equipped items and crew slot keys marked as Evolvers (dump has the
    final augment row for that slot, e.g. ``Ear-Slot6``, ``Primary-Slot5``).
    """
    from inventory_parser.evolver import (
        equipped_item_is_evolver,
        is_evolver_augment_row,
        parent_location_of_evolver_row,
    )

    equipped: dict[str, InventoryItem] = {}
    evolver_keys: set[str] = set()
    current_key_by_base: dict[str, str] = {}
    ear_n = 0
    finger_n = 0
    wrist_n = 0

    for item in data.items:
        loc = item.location

        if is_evolver_augment_row(loc):
            parent = parent_location_of_evolver_row(loc)
            if parent in current_key_by_base:
                key = current_key_by_base[parent]
                if equipped_item_is_evolver(equipped[key].name):
                    evolver_keys.add(key)
            continue

        if "-Slot" in loc:
            continue

        base = loc.split("-")[0].strip()
        if base not in EQUIPMENT_SLOT_BASES:
            continue

        if base == "Ear":
            ear_n += 1
            key = f"Ear-{ear_n}"
        elif base == "Fingers":
            finger_n += 1
            key = f"Fingers-{finger_n}"
        elif base == "Wrist":
            wrist_n += 1
            key = f"Wrist-{wrist_n}"
        else:
            key = base

        equipped[key] = item
        current_key_by_base[base] = key

    return equipped, evolver_keys


def equipped_item_from_inventory(
    item: InventoryItem, *, is_evolver: bool = False
) -> "EquippedItem":
    """Build export row data from a top-level inventory item."""
    from inventory_parser.items import EquippedItem

    return EquippedItem(
        name=item.name,
        item_id=item.item_id,
        is_evolver=is_evolver,
    )
