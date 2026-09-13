from pathlib import Path

from inventory_parser.item_inspect import (
    inspect_from_dict,
    inspect_to_dict,
    parse_item_inspect,
)
from inventory_parser.raid_bis.catalog import parse_item_page

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CHEST_HTML = (FIXTURES / "eqresource_item_inspect_175821.html").read_text(encoding="utf-8")


def test_parse_item_inspect_chest_fixture() -> None:
    card = parse_item_inspect(CHEST_HTML, 175821)
    assert card is not None
    assert card.name == "Exarch Breastplate of Resonant Fracture"
    assert card.icon_id == "5297"
    assert card.expansion_code == "sor"
    assert card.tier == "Raid - Tier 2"
    assert card.flags == ["Magic", "Lore", "No Trade", "Prestige"]
    assert card.classes == "Paladin"
    assert "Drakkin" in card.races
    assert card.slot == "Chest"
    assert card.size == "LARGE"
    assert card.weight == "13.2"
    assert card.tribute == "74876"
    assert card.req_level == "130"
    assert "Type 21 (Armor Ornamentation)" in card.aug_slots_top
    assert "Type 5 (General: Multiple Stat)" in card.aug_slots_bottom
    assert "Type 8 (General: Raid)" in card.aug_slots_bottom
    assert "Power Source" not in card.aug_slots_top
    assert "Power Source" not in card.aug_slots_bottom
    labels = [block.labels[0] for block in card.stat_blocks]
    assert "AC" in labels
    assert "Strength" in labels
    assert "Magic" in labels
    assert "Attack" in labels
    by_first = {block.labels[0]: block for block in card.stat_blocks}
    assert by_first["AC"].values[0] == "1981"
    assert "75" in by_first["AC"].values
    assert "88 + 41" in by_first["Strength"].values
    assert by_first["Magic"].values[0] == "102"
    assert by_first["Attack"].values[0] == "90"
    assert "HP Regen" in by_first["Attack"].labels
    assert "Rousing Zeal" in card.effect
    assert "Deflection Discipline Duration" in card.focus
    assert card.lore == "Exarch Breastplate of Resonant Fracture"


def test_inspect_dict_roundtrip_drops_power_source() -> None:
    parsed = parse_item_inspect(CHEST_HTML, 175821)
    assert parsed is not None
    raw = inspect_to_dict(parsed)
    raw["augSlotsBottom"] = list(raw["augSlotsBottom"]) + ["Power Source"]
    card = inspect_from_dict(raw, item_id=175821)
    assert card is not None
    assert "Power Source" not in card.aug_slots_bottom
    assert "Power Source" not in inspect_to_dict(card)["augSlotsBottom"]


def test_parse_item_page_still_uses_scoring_stats() -> None:
    item = parse_item_page(CHEST_HTML, 175821)
    assert item is not None
    assert item.stats.get("ac") == 1981
    assert item.stats.get("hp") == 24275
    assert item.stats.get("hstr") == 41
    assert "purity" not in item.stats
    assert item.fits_class("PAL")
    assert not item.fits_class("WAR")
