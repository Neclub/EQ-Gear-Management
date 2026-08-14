from inventory_parser.slots import (
    ALL_GEAR_SLOTS,
    AUG_ASSIGNMENT_ORDER,
    EAR_REPORT_SLOTS,
    EQUIPMENT_SLOT_BASES,
    PRIORITY_AUG_SLOTS,
    TEAM_GEAR_SLOTS,
    NON_VISIBLE_SLOTS,
    VISIBLE_SLOTS,
    aug_assignment_order,
    priority_aug_slots,
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


def test_all_gear_slots_matches_equipment_bases() -> None:
    assert ALL_GEAR_SLOTS == EQUIPMENT_SLOT_BASES
    assert "Ear-1" in EAR_REPORT_SLOTS
    assert PRIORITY_AUG_SLOTS == ("Range", "Charm")
    assert AUG_ASSIGNMENT_ORDER[0] == "Range"


def test_priority_aug_slots_without_class() -> None:
    assert priority_aug_slots(None) == ("Range", "Charm")
    order = aug_assignment_order(None)
    assert order[:2] == ("Range", "Charm")
    assert set(order) == set(TEAM_GEAR_SLOTS)
