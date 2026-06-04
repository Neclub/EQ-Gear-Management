from inventory_parser.gear_tiers import UNKNOWN_TIER_LABEL
from inventory_parser.sor_tier import sor_gap_label


def test_sor_gap_labels_by_tier() -> None:
    assert sor_gap_label("Defender's Charm of Rebellion") == "TOB-R2"
    assert sor_gap_label("Dragonbrood Gloves of Shattered Dominion") == "SOR-R1"
    assert sor_gap_label("Bo Staff of Resonant Fracture") == "SOR-R2"


def test_empty_slot_no_label() -> None:
    assert sor_gap_label(None) is None


def test_evolver_shows_evolver_label() -> None:
    assert (
        sor_gap_label("Defender's Charm of Rebellion", is_evolver=True) == "TOB-R2"
    )
    assert (
        sor_gap_label("Dragonbrood Gloves of Shattered Dominion", is_evolver=True)
        == "SOR-R1"
    )
    assert (
        sor_gap_label("Bo Staff of Resonant Fracture", is_evolver=True) == "SOR-R2"
    )
    assert (
        sor_gap_label(
            "Blooded Righteous Protector's Earring of Rallos", is_evolver=True
        )
        == "Evolver"
    )


def test_group_tier_labels() -> None:
    assert sor_gap_label("Diminished Broken Accord Wrist Armor") == "SOR-G1"
    assert sor_gap_label("Defender's Gem of Unraveling Order") == "SOR-G3"


def test_unknown_label() -> None:
    assert sor_gap_label("Radiant Protector's Collar of Legacies Lost") == UNKNOWN_TIER_LABEL
