"""Equipment slot layout for crew gear spreadsheets."""

from __future__ import annotations

from typing import Literal

# Slots shown on the character model (armor view).
VISIBLE_SLOTS: tuple[str, ...] = (
    "Arms",
    "Chest",
    "Feet",
    "Hands",
    "Head",
    "Legs",
    "Wrist-1",
    "Wrist-2",
    "Primary",
    "Secondary",
)

# Equipped slots not on the visible model (jewelry, cloak, etc.).
NON_VISIBLE_SLOTS: tuple[str, ...] = (
    "Back",
    "Charm",
    "Ear-1",
    "Ear-2",
    "Face",
    "Fingers-1",
    "Fingers-2",
    "Neck",
    "Range",
    "Shoulders",
    "Waist",
)

# All crew slots: visible first, then non-visible.
CREW_GEAR_SLOTS: tuple[str, ...] = VISIBLE_SLOTS + NON_VISIBLE_SLOTS

VISIBILITY_VISIBLE = "Visible"
VISIBILITY_NON_VISIBLE = "Non-visible"

SlotFilter = Literal["all", "visible", "non_visible"]

SLOT_VISIBILITY: dict[str, str] = {
    **dict.fromkeys(VISIBLE_SLOTS, VISIBILITY_VISIBLE),
    **dict.fromkeys(NON_VISIBLE_SLOTS, VISIBILITY_NON_VISIBLE),
}

EQUIPMENT_SLOT_BASES: frozenset[str] = frozenset(
    {
        "Charm",
        "Ear",
        "Head",
        "Face",
        "Neck",
        "Shoulders",
        "Arms",
        "Back",
        "Wrist",
        "Range",
        "Hands",
        "Primary",
        "Secondary",
        "Fingers",
        "Chest",
        "Legs",
        "Feet",
        "Waist",
        "Power Source",
        "Ammo",
    }
)


def slots_for_export(slot_filter: SlotFilter = "all") -> tuple[str, ...]:
    """Return slot row order for Excel export."""
    if slot_filter == "visible":
        return VISIBLE_SLOTS
    if slot_filter == "non_visible":
        return NON_VISIBLE_SLOTS
    return CREW_GEAR_SLOTS


def slot_visibility(slot: str) -> str:
    return SLOT_VISIBILITY[slot]
