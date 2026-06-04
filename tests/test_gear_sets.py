import pytest

from inventory_parser.gear_sets import classify_gear_set


@pytest.mark.parametrize(
    ("item", "key"),
    [
        ("Bo Staff of Resonant Fracture", "fracture"),
        ("Dragonbrood Gloves of Shattered Dominion", "shattered_dominion"),
        ("Defender's Charm of Rebellion", "rebellion"),
        ("Exarch Gauntlets of the Bound", "bound"),
        ("Exarch Vambraces of Eternal Reverie", "eternal_reverie"),
        ("Loremaster Helm of Heroic Reflections", "heroic_reflections"),
        ("Spectral Luclinite Charm of Brilliance", "spectral_luclinite"),
        ("Illuminator Bracer of Spectral Luminosity", "spectral_luminosity"),
        ("Luclinite Coagulated War Sword", "luclinite_coagulated"),
    ],
)
def test_classify_known_sets(item: str, key: str) -> None:
    result = classify_gear_set(item)
    assert result is not None
    assert result.key == key


def test_shattered_before_rebellion() -> None:
    result = classify_gear_set("Loremaster Bracer of Shattered Dominion")
    assert result is not None
    assert result.key == "shattered_dominion"


def test_unrecognized_returns_none() -> None:
    assert classify_gear_set("Radiant Protector's Collar of Legacies Lost") is None
