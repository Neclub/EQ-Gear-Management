import pytest

from inventory_parser.gear_tiers import (
    SOR_CURRENT_TIER_CODE,
    UNKNOWN_TIER_LABEL,
    classify_gear_tier,
    tier_code_for_item,
)
from inventory_parser.sor_tier import sor_gap_label


@pytest.mark.parametrize(
    ("item", "code"),
    [
        ("Bo Staff of Resonant Fracture", SOR_CURRENT_TIER_CODE),
        ("Dragonbrood Gloves of Shattered Dominion", "SOR-R1"),
        ("Diminished Broken Accord Wrist Armor", "SOR-G1"),
        ("Acrobat's Gem of Unraveling Order", "SOR-G3"),
        ("Defender's Charm of Rebellion", "TOB-R2"),
        ("Exarch Gauntlets of the Bound", "TOB-R1"),
        ("Obscured Chest Armor of the Shackled", "TOB-G2"),
        ("Adroit Earring of Eternal Reverie", "LS-R2"),
        ("Obscured Gallant Resonance Hands Armor", "LS-G1"),
        ("Spectral Luclinite Charm of Brilliance", "NoS-R2"),
        ("Illuminator Bracer of Spectral Luminosity", "NoS-R1"),
        ("Cloak of Enduring Harmony", "ANI27"),
    ],
)
def test_regex_tier_codes(item: str, code: str) -> None:
    tier = classify_gear_tier(item)
    assert tier is not None
    assert tier.code == code


@pytest.mark.parametrize(
    ("item", "code"),
    [
        ("Broadleaf Belt", "SOR-R1"),
        ("Skyguard's Formal Sash", "TOB-R1"),
        ("Spaulders of the Hand", "LS-R1"),
        ("Hydra Shard Earring", "NoS-R1"),
        ("Mantle of Enduring Harmony", "ANI27"),
        ("Devotee's Enhancement of Enduring Harmony", "ANI27"),
    ],
)
def test_vendor_tier_codes(item: str, code: str) -> None:
    assert tier_code_for_item(item) == code


def test_tradeskill_names_not_classified() -> None:
    assert classify_gear_tier("Fractured Arm Armor Lining") is None
    assert classify_gear_tier("Charm Polishing Cloth of Rebellion") is None
    assert classify_gear_tier("Valiant Belt Buckle") is None
    assert classify_gear_tier("Apparitional Cloak Fastener") is None


def test_fracture_not_fractured_tradeskill() -> None:
    assert tier_code_for_item("Guardian's Ring of Resonant Fracture") == SOR_CURRENT_TIER_CODE
    assert classify_gear_tier("Fractured Tourmaline Earring") is not None
    assert classify_gear_tier("Fractured Tourmaline Earring").code == "SOR-R1"


def test_unknown_tier() -> None:
    assert tier_code_for_item("Radiant Protector's Collar of Legacies Lost") is None
    assert sor_gap_label("Radiant Protector's Collar of Legacies Lost") == UNKNOWN_TIER_LABEL
