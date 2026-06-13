from inventory_parser.slots import (
    TEAM_GEAR_SLOTS,
    NON_VISIBLE_SLOTS,
    VISIBLE_SLOTS,
    slots_for_export,
    slot_visibility,
)


def test_team_slots_visible_then_non_visible() -> None:
    assert TEAM_GEAR_SLOTS[: len(VISIBLE_SLOTS)] == VISIBLE_SLOTS
    assert TEAM_GEAR_SLOTS[len(VISIBLE_SLOTS) :] == NON_VISIBLE_SLOTS


def test_slot_visibility() -> None:
    assert slot_visibility("Arms") == "Visible"
    assert slot_visibility("Charm") == "Non-visible"


def test_slots_for_export_filters() -> None:
    assert slots_for_export("visible") == VISIBLE_SLOTS
    assert slots_for_export("non_visible") == NON_VISIBLE_SLOTS
    assert slots_for_export("all") == TEAM_GEAR_SLOTS
