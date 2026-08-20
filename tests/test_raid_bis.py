from pathlib import Path

from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.html_export import extract_report_json, write_team_html
from inventory_parser.items import EquippedItem
from inventory_parser.raid_bis.catalog import parse_raidarmor_html, parse_raidgear_html, parse_item_page
from inventory_parser.raid_bis.compare import (
    build_ideal_loadout,
    compare_character,
    format_stat_deltas,
    score_stats,
)
from inventory_parser.raid_bis.models import RaidGearCandidate
from inventory_parser.slot2_augs.weights import resolve_weights
from inventory_parser.team_report import CharacterGear

FIXTURES = Path(__file__).resolve().parent / "fixtures"
EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
ARMOR_HTML = FIXTURES / "eqresource_raidarmor_sor.html"
GEAR_HTML = FIXTURES / "eqresource_raidgear_sor.html"


def _cand(**kwargs) -> RaidGearCandidate:
    return RaidGearCandidate(**kwargs)


def test_parse_raidarmor_class_locked_chest():
    items = parse_raidarmor_html(ARMOR_HTML.read_text(encoding="utf-8"))
    war = [i for i in items if i.fits_slot("Chest") and i.fits_class("WAR")]
    clr = [i for i in items if i.fits_slot("Chest") and i.fits_class("CLR")]
    assert war
    assert clr
    assert {i.item_id for i in war}.isdisjoint({i.item_id for i in clr})
    loadout = build_ideal_loadout(items, class_abbr="WAR")
    chest = loadout.get("Chest")
    assert chest is not None
    assert chest.fits_class("WAR")
    assert not chest.fits_class("CLR")


def test_parse_raidgear_back_table():
    items = parse_raidgear_html(
        GEAR_HTML.read_text(encoding="utf-8"),
        default_slot="Back",
    )
    names = {i.name for i in items}
    assert "Ice Veined Fire Cloak" in names
    cloak = next(i for i in items if i.item_id == 175726)
    assert cloak.stats.get("ac") == 879
    assert cloak.icon_id == "3684"
    assert "Back" in cloak.slots


def test_t1_can_beat_t2_on_weights():
    t1 = _cand(
        item_id=1,
        name="T1 Chest",
        stats={"ac": 1200, "hdex": 20},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Chest"}),
        tier="T1",
    )
    t2 = _cand(
        item_id=2,
        name="T2 Chest",
        stats={"ac": 800, "hdex": 40},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Chest"}),
        tier="T2",
    )
    weights = resolve_weights("WAR", "Chest")
    assert score_stats(t1.stats, weights) > score_stats(t2.stats, weights)
    loadout = build_ideal_loadout([t1, t2], class_abbr="WAR")
    assert loadout["Chest"].item_id == 1


def test_displayed_stat_deltas_are_trimmed():
    deltas = {
        "ac": 75,
        "hp": 4047,
        "mana": 4206,
        "endurance": 4206,
        "hdex": 17,
        "hint": 6,
        "hwis": 5,
        "spell_damage": -54,
        "heal_amount": 79,
    }
    pal = format_stat_deltas(deltas, class_abbr="PAL")
    assert pal == "+75 AC, +4047 HP, +4206 Mana, +17 HDex"
    assert "Spell Damage" not in pal
    war = format_stat_deltas(deltas, class_abbr="WAR")
    assert war == "+75 AC, +4047 HP, +17 HDex"
    assert "Mana" not in war
    shd = format_stat_deltas(deltas, class_abbr="SHD")
    assert shd == pal
    mnk = format_stat_deltas(deltas, class_abbr="MNK")
    assert mnk == "+4047 HP, +17 HDex"
    assert "AC" not in mnk
    assert "Mana" not in mnk
    rog = format_stat_deltas(deltas, class_abbr="ROG")
    assert rog == mnk
    ber = format_stat_deltas(deltas, class_abbr="BER")
    assert ber == mnk
    mag = format_stat_deltas(deltas, class_abbr="MAG")
    assert mag == "+4047 HP, +4206 Mana, +6 HInt, -54 Spell Damage"
    clr = format_stat_deltas(deltas, class_abbr="CLR")
    assert clr == "+4047 HP, +4206 Mana, +5 HWis, -54 Spell Damage"


def test_mag_pins_pet_focus_ear():
    focus = _cand(
        item_id=175913,
        name="Summoner's Earring of Resonant Fracture",
        stats={"spell_damage": 170, "hint": 71, "ac": 515},
        classes=frozenset({"MAG", "BST", "NEC"}),
        slots=frozenset({"Ear"}),
        tier="T2",
        focus="Enhanced Minion XXXVIII",
        lore_group="summoner-t2",
    )
    t1_focus = _cand(
        item_id=175713,
        name="Flame-Dipped Jasper Ear Spike",
        stats={"spell_damage": 148, "hint": 71, "ac": 505},
        classes=frozenset({"MAG", "BST", "NEC"}),
        slots=frozenset({"Ear"}),
        tier="T1",
        focus="Enhanced Minion XXXVII",
        lore_group="flame-t1",
    )
    fancy = _cand(
        item_id=99,
        name="Fancy Caster Stud",
        stats={"spell_damage": 400, "hint": 90, "ac": 900},
        classes=frozenset({"MAG", "WIZ", "ENC"}),
        slots=frozenset({"Ear"}),
        tier="T2",
        lore_group="fancy",
    )
    loadout = build_ideal_loadout([focus, t1_focus, fancy], class_abbr="MAG")
    ear_ids = {loadout[s].item_id for s in ("Ear-1", "Ear-2") if s in loadout}
    assert 175913 in ear_ids
    assert loadout["Ear-1"].is_pet_focus_ear() or loadout["Ear-2"].is_pet_focus_ear()


def test_war_is_not_pinned_to_pet_focus():
    focus = _cand(
        item_id=175913,
        name="Summoner's Earring of Resonant Fracture",
        stats={"ac": 515, "hdex": 41},
        classes=frozenset({"MAG", "BST", "NEC"}),
        slots=frozenset({"Ear"}),
        focus="Enhanced Minion XXXVIII",
    )
    war_ear = _cand(
        item_id=50,
        name="Plate Stud",
        stats={"ac": 900, "hdex": 50},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    loadout = build_ideal_loadout([focus, war_ear], class_abbr="WAR")
    for slot in ("Ear-1", "Ear-2"):
        if slot in loadout:
            assert loadout[slot].item_id != 175913
            assert not loadout[slot].is_pet_focus_ear()


def test_lore_uniqueness_for_dual_ears():
    a = _cand(
        item_id=10,
        name="Shared Lore Ear",
        stats={"ac": 100, "hdex": 10},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
        lore_group="same-lore",
    )
    b = _cand(
        item_id=11,
        name="Shared Lore Ear Twin",
        stats={"ac": 90, "hdex": 9},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
        lore_group="same-lore",
    )
    c = _cand(
        item_id=12,
        name="Other Ear",
        stats={"ac": 80, "hdex": 8},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
        lore_group="other",
    )
    loadout = build_ideal_loadout([a, b, c], class_abbr="WAR")
    keys = {loadout[s].lore_key() for s in ("Ear-1", "Ear-2") if s in loadout}
    assert "same-lore" in keys
    assert len(keys) == len(loadout.keys() & {"Ear-1", "Ear-2"})


def test_equipped_bis_ear_is_not_recommended_for_the_other_ear() -> None:
    best = _cand(
        item_id=10,
        name="Best Ear",
        stats={"ac": 100, "hdex": 20},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    second = _cand(
        item_id=11,
        name="Second Ear",
        stats={"ac": 90, "hdex": 15},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    third = _cand(
        item_id=12,
        name="Third Ear",
        stats={"ac": 80, "hdex": 10},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    equipped = {
        "Ear-2": EquippedItem(name=best.name, item_id=best.item_id),
    }
    loadout = build_ideal_loadout(
        [best, second, third], class_abbr="WAR", equipped=equipped
    )
    assert loadout["Ear-2"].item_id == 10
    assert loadout["Ear-1"].item_id == 11


def test_equipped_second_ear_is_not_suggested_for_the_other_slot() -> None:
    best = _cand(
        item_id=10,
        name="Best Ear",
        stats={"ac": 100, "hdex": 20},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    second = _cand(
        item_id=11,
        name="Second Ear",
        stats={"ac": 90, "hdex": 15},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    third = _cand(
        item_id=12,
        name="Third Ear",
        stats={"ac": 80, "hdex": 10},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Ear"}),
    )
    equipped = {
        "Ear-1": EquippedItem(name=second.name, item_id=second.item_id),
    }
    loadout = build_ideal_loadout(
        [best, second, third], class_abbr="WAR", equipped=equipped
    )
    assert loadout["Ear-1"].item_id == 10
    assert loadout["Ear-2"].item_id == 12
    ch = CharacterGear(character="Warlub", server="test", filepath="x", class_abbr="WAR")
    ch.slots["Ear-1"] = EquippedItem(name=second.name, item_id=second.item_id)
    report = compare_character(ch, [best, second, third])
    by_slot = {row.gear_slot: row for row in report.slots}
    assert by_slot["Ear-1"].recommended_id == 10
    assert by_slot["Ear-2"].recommended_id == 12
    assert by_slot["Ear-2"].recommended_id != second.item_id


def test_equipped_ring_is_not_recommended_for_the_other_finger() -> None:
    best = _cand(
        item_id=30,
        name="Best Ring",
        stats={"ac": 100, "hdex": 20},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Fingers"}),
    )
    second = _cand(
        item_id=31,
        name="Second Ring",
        stats={"ac": 90, "hdex": 15},
        classes=frozenset({"WAR"}),
        slots=frozenset({"Fingers"}),
    )
    equipped = {
        "Fingers-2": EquippedItem(name=best.name, item_id=best.item_id),
    }
    loadout = build_ideal_loadout([best, second], class_abbr="WAR", equipped=equipped)
    assert loadout["Fingers-2"].item_id == 30
    assert loadout["Fingers-1"].item_id == 31


def test_wrists_can_equip_the_same_item():
    bracer = _cand(
        item_id=20,
        name="Exarch Bracer of Resonant Fracture",
        stats={"ac": 100, "hdex": 10, "hp": 2000},
        classes=frozenset({"PAL"}),
        slots=frozenset({"Wrist"}),
        lore_group="exarch-bracer",
    )
    weaker = _cand(
        item_id=21,
        name="Lesser Bracer",
        stats={"ac": 50, "hdex": 5, "hp": 500},
        classes=frozenset({"PAL"}),
        slots=frozenset({"Wrist"}),
        lore_group="lesser-bracer",
    )
    loadout = build_ideal_loadout([bracer, weaker], class_abbr="PAL")
    assert loadout["Wrist-1"].item_id == 20
    assert loadout["Wrist-2"].item_id == 20


def test_paperdoll_follows_inventory_window():
    from inventory_parser.raid_bis.models import PAPERDOLL_SLOTS

    assert PAPERDOLL_SLOTS[:4] == ("Ear-1", "Head", "Face", "Ear-2")
    assert PAPERDOLL_SLOTS[4:6] == ("Chest", "Neck")
    assert PAPERDOLL_SLOTS[12:16] == ("Legs", "Hands", "Charm", "Feet")
    assert PAPERDOLL_SLOTS[-4:] == ("Primary", "Secondary", "Range", "Ammo")
    assert "Power Source" in PAPERDOLL_SLOTS
    catalog = [
        _cand(
            item_id=2,
            name="BiS Chest",
            stats={"ac": 100, "hdex": 10},
            classes=frozenset({"WAR"}),
            slots=frozenset({"Chest"}),
        )
    ]
    ch = CharacterGear(
        character="Warlub",
        server="test",
        filepath="x",
        class_abbr="WAR",
    )
    ch.slots["Chest"] = EquippedItem(name="Old Chest", item_id=1)
    ch.slots["Power Source"] = EquippedItem(name="Glowing Orb", item_id=99)
    ch.slots["Ammo"] = EquippedItem(name="Arrow", item_id=88)
    report = compare_character(
        ch,
        catalog,
        equipped_stats={
            1: _cand(
                item_id=1,
                name="Old Chest",
                stats={"ac": 40, "hdex": 4},
                slots=frozenset({"Chest"}),
                icon_id="10",
            ),
            99: _cand(item_id=99, name="Glowing Orb", icon_id="50"),
        },
    )
    order = [s.gear_slot for s in report.slots]
    assert order == list(PAPERDOLL_SLOTS)
    power = next(s for s in report.slots if s.gear_slot == "Power Source")
    assert power.status == "weapon"
    assert power.scored is False
    assert power.current_name == "Glowing Orb"
    assert power.current_icon_id == "50"
    ammo = next(s for s in report.slots if s.gear_slot == "Ammo")
    assert ammo.current_name == "Arrow"
    chest = next(s for s in report.slots if s.gear_slot == "Chest")
    assert chest.status == "upgrade"
    assert chest.deltas["ac"] == 60
    assert chest.deltas["hdex"] == 6
    assert report.total_deltas["ac"] == 60


def test_html_section_present(tmp_path: Path):
    inv = EXAMPLES / "Deflub_bristle-Inventory.txt"
    bundle = build_export_bundle(
        [inv],
        include_spells=False,
        include_achievements=False,
        include_slot2=False,
        include_raid_bis=True,
        raid_bis_html_overrides={
            "raidarmor": ARMOR_HTML.read_text(encoding="utf-8"),
            "raidgear:back": GEAR_HTML.read_text(encoding="utf-8"),
        },
        raid_bis_allow_network=False,
        raid_bis_hydrate=False,
        raid_bis_embed_icons=False,
    )
    out = tmp_path / "raid.html"
    write_team_html(bundle, out)
    report = extract_report_json(out.read_text(encoding="utf-8"))
    ids = [s["id"] for s in report["sections"]]
    assert "raid_bis" in ids
    section = next(s for s in report["sections"] if s["id"] == "raid_bis")
    assert section["data"]["characters"]
    html = out.read_text(encoding="utf-8")
    assert "raid-bis-legend" in html
    assert "Current raid gear only. Evolvers are not scored and may still be BiS." in html
    assert "Green: already BiS" in html
    assert "Gold: upgrade" in html
    assert "s-powersource" in html
    assert "s-fingers1 { grid-column: 2; grid-row: 7; }" in html
    assert "section.type === \"raid_bis\" && (section.data.characters || []).length" in html
    assert "state.chars.raid_bis" in html
    assert "Most upgrades" not in html


def test_parse_item_page_pet_focus():
    html = """
    <font size="+1"><b><center>Summoner's Earring of Resonant Fracture<br><br></center></b></font>
    Class: Beastlord, Magician, Necromancer
    Slot: Ear
    Focus: Enhanced Minion XXXVIII
    <img src="itemimages/1642.png">
    <td>AC:<br>HP:<br>Mana:<br>End:<br></td>
    <td>515<br>20871<br>22831<br>22831<br></td>
    Raid - Tier 2
    """
    item = parse_item_page(html, 175913)
    assert item is not None
    assert item.is_pet_focus_ear()
    assert "MAG" in item.classes
    assert item.stats.get("ac") == 515
    assert item.tier == "T2"


def test_item_page_parses_ac_hp_when_purity_present():
    html = """
    <font size="+1"><b><center>Exarch Breastplate of Resonant Fracture<br><br></center></b></font>
    Class: Paladin
    Slot: Chest
    <td>AC:<br>HP:<br>Mana:<br>End:<br>Purity:<br></td>
    <td>1981<br>24275<br>22408<br>22408<br>75<br></td>
    Raid - Tier 2
    """
    item = parse_item_page(html, 175821)
    assert item is not None
    assert item.stats.get("ac") == 1981
    assert item.stats.get("hp") == 24275
    assert item.stats.get("mana") == 22408
    assert item.fits_class("PAL")
    assert not item.fits_class("WAR")


def test_item_page_parses_spell_damage_without_attack():
    html = """
    <font size="+1"><b><center>Frostfire Robe of Resonant Fracture<br><br></center></b></font>
    Class: Wizard
    Slot: Chest
    <td>AC:<br>HP:<br>Mana:<br>End:<br>Purity:<br></td>
    <td>530<br>22174<br>24290<br>24290<br>75<br></td>
    <td>HP Regen:<br>Mana Regen:<br>Heal Amount:<br>Spell Damage:<br>Clairvoyance:<br></td>
    <td>24<br>16<br>79<br>139<br>185<br></td>
    Raid - Tier 2
    """
    item = parse_item_page(html, 175884)
    assert item is not None
    assert item.stats.get("spell_damage") == 139
    assert item.stats.get("heal_amount") == 79
    assert item.stats.get("clairvoyance") == 185
    assert format_stat_deltas(
        {"hp": 1546, "mana": 1200, "hint": 2, "spell_damage": 14},
        class_abbr="WIZ",
    ) == "+1546 HP, +1200 Mana, +2 HInt, +14 Spell Damage"


def test_item_page_parses_spell_damage_with_luck_and_backstab():
    html = """
    <font size="+1"><b><center>Mystic's Cloak of Resonant Fracture<br><br></center></b></font>
    Class: All
    Slot: Back
    <td>Luck:<br>Attack:<br>HP Regen:<br>Mana Regen:<br>End Regen:<br>Heal Amount:<br>Spell Damage:<br>Clairvoyance:<br>Backstab:<br></td>
    <td>38-40<br>90<br>25<br>15<br>1<br>159<br>138<br>185<br>20<br></td>
    Raid - Tier 2
    """
    item = parse_item_page(html, 175927)
    assert item is not None
    assert item.stats.get("spell_damage") == 138
    assert item.stats.get("heal_amount") == 159
    assert item.stats.get("atk") == 90
    assert item.stats.get("clairvoyance") == 185


def test_all_class_jewelry_is_legal():
    cloak = _cand(
        item_id=175926,
        name="Guardian's Cloak of Resonant Fracture",
        stats={"ac": 896, "hp": 22784, "hdex": 41},
        classes=frozenset(),
        slots=frozenset({"Back"}),
        tier="T2",
    )
    loadout = build_ideal_loadout([cloak], class_abbr="PAL")
    assert loadout["Back"].item_id == 175926
