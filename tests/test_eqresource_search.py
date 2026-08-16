"""Tests for EQ Resource advanced-search catalog parsing."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.slot2_augs.eqresource_search import (
    eqresource_search_payload,
    fetch_eqresource_catalog,
    parse_eqresource_search_html,
)
from inventory_parser.slot2_augs.raidloot import unique_by_lore_group

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SEARCH = FIXTURES / "eqresource_search_int_snip.html"

_MYSTIC_ITEM = """
<font size="+1"><b><center>Mystic's Gem of Unraveling Order<br><br></center></b></font>
Slot: Arms, Back, Chest, Ear, Face, Feet, Finger, Hands, Head, Legs, Neck, Shoulder, Waist, Wrist
<td>AC:<br>HP:<br>Mana:<br>End:<br></td>
<td>115<br>1470<br>2040<br>2040<br></td>
Lore Group: <a href="itemsearch.php?loregroup=Intellect or Might of Unraveling Order">Intellect or Might of Unraveling Order</a>
"""

_DEFENDER_ITEM = """
<font size="+1"><b><center>Defender's Gem of Unraveling Order<br><br></center></b></font>
Slot: Arms, Back, Chest, Ear, Face, Feet, Finger, Hands, Head, Legs, Neck, Shoulder, Waist, Wrist
<td>AC:<br>HP:<br>Mana:<br>End:<br></td>
<td>115<br>2040<br>1470<br>1470<br></td>
Lore Group: <a href="itemsearch.php?loregroup=Intellect or Might of Unraveling Order">Intellect or Might of Unraveling Order</a>
"""


def test_eqresource_search_payload_int_spell_damage():
    payload = eqresource_search_payload("int", augtype="7")
    assert payload["type"] == "augs"
    assert payload["augtype"] == "7"
    assert payload["augslot"] == "7"
    assert payload["augmentation"] == "1"
    assert payload["attrib1"] == "spelldamage"
    assert payload["attrib1range"] == "greater"
    assert payload["attrib1amt"] == "80"
    assert payload["attrib2"] == "hintel"
    assert payload["attrib3"] == "hdex"
    assert payload["attrib4"] == "hwis"


def test_parse_eqresource_search_html_stats():
    rows = parse_eqresource_search_html(SEARCH.read_text(encoding="utf-8"))
    by_id = {r.item_id: r for r in rows}
    assert set(by_id) >= {88785, 175573, 175571, 175572}
    mystic = by_id[175573]
    assert mystic.name.startswith("Mystic")
    assert mystic.stats.get("spell_damage") == 118
    assert mystic.stats.get("hint") == 61
    assert mystic.stats.get("hwis") == 61
    assert mystic.stats.get("ac") == 115
    assert mystic.stats.get("hp") == 1470
    defender = by_id[175571]
    assert defender.stats.get("spell_damage") == 111
    assert defender.stats.get("hp") == 2040


def test_eqresource_catalog_hydrates_lore_group():
    cat = fetch_eqresource_catalog(
        "int",
        html_override=SEARCH.read_text(encoding="utf-8"),
        item_html_by_id={175573: _MYSTIC_ITEM, 175571: _DEFENDER_ITEM},
        allow_network=False,
    )
    by_id = {a.item_id: a for a in cat.augs}
    assert by_id[175573].lore_group == "Intellect or Might of Unraveling Order"
    assert by_id[175571].lore_group == "Intellect or Might of Unraveling Order"
    assert by_id[175573].stats.get("spell_damage") == 118
    kept = unique_by_lore_group(
        [by_id[175573], by_id[175571], by_id[88785]]
    )
    assert [a.item_id for a in kept] == [175573, 88785]


def test_eqresource_catalog_drops_type5_after_hydrate():
    green = (FIXTURES / "eqresource_aug_173378.html").read_text(encoding="utf-8")
    search = SEARCH.read_text(encoding="utf-8").replace(
        "</table>\n</td></tr>",
        '<tr><td bgcolor="#111111"><img src="itemimages/6467.png"></td>'
        '<td bgcolor="#111111"><a href=items.php?id=173378>Immovable Green Gem</a></td>'
        "<td>0</td><td>0</td><td>0</td><td>0</td>"
        "<td>0</td><td>63</td><td>41</td><td>63</td></tr>\n</table>\n</td></tr>",
        1,
    )
    assert 173378 in {r.item_id for r in parse_eqresource_search_html(search)}
    cat = fetch_eqresource_catalog(
        "wis",
        html_override=search,
        item_html_by_id={173378: green, 175573: _MYSTIC_ITEM, 175571: _DEFENDER_ITEM},
        allow_network=False,
    )
    ids = {a.item_id for a in cat.augs}
    assert 173378 not in ids
    assert 175573 in ids
