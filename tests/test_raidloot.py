"""Tests for raidloot slot-restriction parsing and HTML catalog parse."""

from __future__ import annotations

import json
from pathlib import Path

from inventory_parser.slot2_augs.raidloot import (
    AugCandidate,
    CatalogResult,
    augs_for_slot,
    _candidate_to_dict,
    fetch_catalog,
    merge_shield_augs,
    parse_raidloot_html,
    parse_raidloot_lore_group,
    parse_shield_html,
    parse_slot_restrictions,
    unique_by_lore_group,
)
from inventory_parser.slot2_augs.profiles import ARTISANS_PRIZE_ID, SHIELD_AUG_URL

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "raidloot_dex_sample.html"
SHIELD_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "raidloot_shield_snip.html"


def _stub_eqr_catalog(profile: str = "dex") -> CatalogResult:
    """Minimal EQ Resource-shaped catalog so fetch_catalog skips raidloot main list."""
    from inventory_parser.slot2_augs.profiles import ProfileId

    pid: ProfileId = profile  # type: ignore[assignment]
    augs = [
        AugCandidate(
            item_id=ARTISANS_PRIZE_ID,
            name="Artisan's Prize",
            profile=pid,
            focus_heroic=150,
            ear_only=True,
        ),
        AugCandidate(
            item_id=100001,
            name="Stub Gem A",
            profile=pid,
            focus_heroic=50,
            ac=100,
            hp=1000,
            aug_types=frozenset({7, 8}),
        ),
        AugCandidate(
            item_id=100002,
            name="Stub Gem B",
            profile=pid,
            focus_heroic=40,
            ac=90,
            hp=900,
            aug_types=frozenset({7, 8}),
        ),
        AugCandidate(
            item_id=100003,
            name="Stub Gem C",
            profile=pid,
            focus_heroic=30,
            ac=80,
            hp=800,
            aug_types=frozenset({7, 8}),
        ),
    ]
    return CatalogResult(
        profile=pid,
        augs=augs,
        fetched_at="2026-01-01T00:00:00+00:00",
        from_cache=True,
        url="https://items.eqresource.com/dosearch.php",
    )


def _write_shield_cache(cache_file: Path, shields: list[AugCandidate]) -> None:
    cache_file.write_text(
        json.dumps(
            {
                "shield": {
                    "fetched_at": "2026-01-01T00:00:00+00:00",
                    "url": SHIELD_AUG_URL,
                    "augs": [_candidate_to_dict(a) for a in shields],
                }
            }
        ),
        encoding="utf-8",
    )


def test_parse_all_except_charm_range():
    excluded, allowed, ear_only = parse_slot_restrictions(
        "All except Charm, Range, Primary, Secondary, Ammo"
    )
    assert ear_only is False
    assert allowed == frozenset()
    assert excluded == frozenset({"Charm", "Range", "Primary", "Secondary", "Ammo"})


def test_parse_fits_charm_and_range():
    excluded, allowed, ear_only = parse_slot_restrictions(
        "All except Primary, Secondary, Ammo"
    )
    assert "Charm" not in excluded
    assert "Range" not in excluded


def test_parse_ear_only():
    excluded, allowed, ear_only = parse_slot_restrictions("Ear")
    assert ear_only is True
    assert allowed == frozenset({"Ear"})


def test_parse_except_range_only_fits_charm():
    excluded, _, _ = parse_slot_restrictions(
        "All except Range, Primary, Secondary, Ammo"
    )
    assert "Range" in excluded
    assert "Charm" not in excluded


def test_parse_html_fixture():
    html = FIXTURE.read_text(encoding="utf-8")
    augs = parse_raidloot_html(html, "dex")
    by_id = {a.item_id: a for a in augs}
    assert ARTISANS_PRIZE_ID in by_id
    assert by_id[ARTISANS_PRIZE_ID].ear_only is True
    assert by_id[175572].excluded_bases >= frozenset({"Charm", "Range"})
    assert "Charm" not in by_id[175169].excluded_bases  # Joy of the Dancer fits Charm
    assert "Range" not in by_id[175169].excluded_bases
    assert by_id[175572].stats.get("hdex") == 61
    assert by_id[175572].stats.get("ac") == 115
    assert by_id[175572].stats.get("hp") == 1750
    assert by_id[175572].stats.get("atk") == 68
    assert by_id[175572].stats.get("heal_amount") == 108
    assert by_id[175572].stats.get("spell_damage") == 114
    assert by_id[175572].stats.get("clairvoyance") == 139
    assert by_id[ARTISANS_PRIZE_ID].stats.get("hdex") == 150


def test_parse_live_style_detail_divs():
    html = (
        Path(__file__).resolve().parent / "fixtures" / "raidloot_dex_live_snippet.html"
    ).read_text(encoding="utf-8")
    augs = parse_raidloot_html(html, "dex")
    by_id = {a.item_id: a for a in augs}
    assert 175572 in by_id
    assert by_id[175572].name.startswith("Acrobat")
    assert by_id[175572].focus_heroic == 61
    assert by_id[175572].ac == 115
    assert by_id[175572].lore is True
    assert "Charm" in by_id[175572].excluded_bases
    assert "Range" in by_id[175572].excluded_bases


def test_augs_for_charm_excludes_common_tops():
    html = FIXTURE.read_text(encoding="utf-8")
    augs = parse_raidloot_html(html, "dex")
    charm = augs_for_slot(augs, "Charm")
    ids = {a.item_id for a in charm}
    assert 175572 not in ids  # Acrobat's excludes Charm
    assert 175169 in ids  # Joy of the Dancer fits
    assert 166898 in ids  # Finesse gem excludes Range only — fits Charm


def test_augs_for_range():
    html = FIXTURE.read_text(encoding="utf-8")
    augs = parse_raidloot_html(html, "dex")
    range_augs = augs_for_slot(augs, "Range")
    ids = {a.item_id for a in range_augs}
    assert 175572 not in ids
    assert 166898 not in ids  # excludes Range
    assert 175169 in ids


def test_parse_secondary_slot_only():
    excluded, allowed, ear_only = parse_slot_restrictions("Secondary")
    assert ear_only is False
    assert allowed == frozenset({"Secondary"})
    assert excluded == frozenset()


def test_parse_shield_html_fixture():
    html = SHIELD_FIXTURE.read_text(encoding="utf-8")
    augs = parse_shield_html(html, "dex")
    assert augs
    assert all(a.shield_only for a in augs)
    assert all(a.fits_gear_slot("Secondary") for a in augs)
    assert all(not a.fits_gear_slot("Head") for a in augs)
    by_id = {a.item_id: a for a in augs}
    assert 175179 in by_id
    assert by_id[175179].name.startswith("Votive")
    assert by_id[175179].ac == 113


def test_merge_shield_augs_into_catalog():
    dex = parse_raidloot_html(FIXTURE.read_text(encoding="utf-8"), "dex")
    shields = parse_shield_html(SHIELD_FIXTURE.read_text(encoding="utf-8"), "dex")
    merged = merge_shield_augs(dex, shields)
    assert any(a.shield_only and a.item_id == 175179 for a in merged)
    # Shield augs must not appear as fits for Head
    head_ids = {a.item_id for a in augs_for_slot(merged, "Head")}
    assert 175179 not in head_ids
    sec = augs_for_slot(merged, "Secondary")
    assert any(a.item_id == 175179 and a.shield_only for a in sec)


def test_parse_raidloot_spell_dmg_label():
    """Live raidloot uses ``Spell Dmg:``, not ``Spell Damage:``."""
    html = """
    <table><tr><td></td><td>
    Arcane Gem of Unraveling Order Aug: 7 8 P — 199001 MAGIC LORE NO TRADE PRESTIGE
    Slot: All except Charm, Range, Primary, Secondary, Ammo
    AC: 100 HP: 1500 ATK: 50 INT: 0 + 55
    Heal Amount: 90 Spell Dmg: 114 Clairvoyance: 130
    Required level of 130. Class: All
    </td></tr></table>
    """
    augs = parse_raidloot_html(html, "int")
    gem = next(a for a in augs if a.item_id == 199001)
    assert gem.stats.get("spell_damage") == 114
    assert gem.stats.get("heal_amount") == 90
    assert gem.stats.get("clairvoyance") == 130
    assert gem.stats.get("hint") == 55


def test_parse_raidloot_spell_dmg_html_label():
    html = """
    <table><tr><td></td><td>
    <div class="item augment" data-id="199002">
    <span class="itemname">Arcane Gem of Unraveling Order</span>
    <label>Slot:</label> All except Charm, Range, Primary, Secondary, Ammo<br/>
    <label>AC:</label> 100<br/><label>HP:</label> 1500<br/><label>ATK:</label> 50<br/>
    <label>INT:</label> 0 <span class="heroic">+ 55</span><br/>
    <label>Heal Amount:</label> 90<br/>
    <label>Spell Dmg:</label> 114<br/>
    <label>Clairvoyance:</label> 130<br/>
    </div></td></tr>
    """
    augs = parse_raidloot_html(html, "int")
    gem = next(a for a in augs if a.item_id == 199002)
    assert gem.stats.get("spell_damage") == 114
    assert gem.stats.get("hint") == 55
    assert gem.focus_heroic == 55


def test_parse_raidloot_lore_group_plain_and_label():
    assert parse_raidloot_lore_group(
        "PRESTIGE Lore Equipped Group: 175571 Slot: All except Charm, Range"
    ) == "175571"
    labeled = (
        '<span class="itemflag">PRESTIGE</span> '
        "<label>Lore Equipped Group:</label> 175571"
        "<label>Slot:</label> All except Charm, Range, Primary, Secondary, Ammo"
    )
    assert parse_raidloot_lore_group(labeled) == "175571"
    assert parse_raidloot_lore_group("Slot: Ear AC: 300") is None
    # Live list rows often glue the id to the next label: "175571Slot:"
    assert parse_raidloot_lore_group(
        "PRESTIGE Lore Equipped Group: 175571Slot: All except Charm, Range"
    ) == "175571"


def test_parse_html_lore_group_on_candidate():
    html = """
    <table><tr class="details"><td colspan="99"><div id="item175571"
    class="item augment augment0" data-id="175571">
    <span class="itemname">Defender's Gem of Unraveling Order</span>
    <span class="note">Aug: 7 8</span><span class="note"> — 175571</span>
    <span class="itemflag">LORE</span>
    <label>Lore Equipped Group:</label> 175571
    <label>Slot:</label> All except Charm, Range, Primary, Secondary, Ammo<br/>
    <label>AC:</label> 115<br/><label>HP:</label> 2040<br/><label>ATK:</label> 68<br/>
    <label>STR:</label> 0 <span class="heroic">+ 61</span>
    </div></td></tr>
    <tr class="details"><td colspan="99"><div id="item175573"
    class="item augment augment0" data-id="175573">
    <span class="itemname">Mystic's Gem of Unraveling Order</span>
    <span class="note">Aug: 7 8</span><span class="note"> — 175573</span>
    <span class="itemflag">LORE</span>
    <label>Lore Equipped Group:</label> 175571
    <label>Slot:</label> All except Charm, Range, Primary, Secondary, Ammo<br/>
    <label>AC:</label> 115<br/><label>HP:</label> 1470<br/><label>ATK:</label> 68<br/>
    <label>INT:</label> 0 <span class="heroic">+ 61</span>
    <label>WIS:</label> 0 <span class="heroic">+ 61</span>
    <label>Spell Dmg:</label> 118
    </div></td></tr></table>
    """
    augs = parse_raidloot_html(html, "int")
    by_id = {a.item_id: a for a in augs}
    assert by_id[175571].lore_group == "175571"
    assert by_id[175573].lore_group == "175571"


def test_unique_by_lore_group_keeps_first():
    mystic = AugCandidate(
        item_id=175573,
        name="Mystic's Gem of Unraveling Order",
        profile="int",
        focus_heroic=61,
        lore_group="175571",
    )
    defender = AugCandidate(
        item_id=175571,
        name="Defender's Gem of Unraveling Order",
        profile="int",
        focus_heroic=0,
        lore_group="175571",
    )
    acrobat = AugCandidate(
        item_id=175572,
        name="Acrobat's Gem of Unraveling Order",
        profile="int",
        focus_heroic=0,
    )
    kept = unique_by_lore_group([mystic, defender, acrobat])
    assert [a.item_id for a in kept] == [175573, 175572]


def test_fetch_catalog_uses_shield_disk_cache_before_network(tmp_path, monkeypatch):
    from inventory_parser.slot2_augs.raidloot import cache_path

    monkeypatch.setattr(
        "inventory_parser.slot2_augs.raidloot.appdata_dir",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "inventory_parser.slot2_augs.eqresource_search.fetch_eqresource_catalog",
        lambda profile, **_kwargs: _stub_eqr_catalog(profile),
    )

    def boom(*_args, **_kwargs):
        raise AssertionError("warm shield cache must not hit raidloot")

    monkeypatch.setattr("inventory_parser.slot2_augs.raidloot._http_get", boom)

    shields = parse_shield_html(SHIELD_FIXTURE.read_text(encoding="utf-8"), "dex")
    _write_shield_cache(cache_path(), shields)

    cat = fetch_catalog("dex")
    assert any(a.item_id == 175179 and a.shield_only for a in cat.augs)
    # Main catalog came from EQ Resource stub (from_cache); shield hit is log-only.
    assert cat.from_cache is True


def test_fetch_catalog_force_refresh_fetches_shield(tmp_path, monkeypatch):
    from inventory_parser.slot2_augs.raidloot import cache_path

    monkeypatch.setattr(
        "inventory_parser.slot2_augs.raidloot.appdata_dir",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "inventory_parser.slot2_augs.eqresource_search.fetch_eqresource_catalog",
        lambda profile, **_kwargs: _stub_eqr_catalog(profile),
    )

    hits: list[str] = []

    def fake_get(url: str, timeout: float = 30.0) -> str:
        hits.append(url)
        assert "Aug_Shield" in url or "augslot" in url
        return SHIELD_FIXTURE.read_text(encoding="utf-8")

    monkeypatch.setattr("inventory_parser.slot2_augs.raidloot._http_get", fake_get)

    shields = parse_shield_html(SHIELD_FIXTURE.read_text(encoding="utf-8"), "dex")
    _write_shield_cache(cache_path(), shields)

    cat = fetch_catalog("dex", force_refresh=True)
    assert hits
    assert any(a.item_id == 175179 and a.shield_only for a in cat.augs)


def test_fetch_catalog_shield_live_failure_uses_disk_fallback(tmp_path, monkeypatch):
    """Cold in-memory load + live failure still picks up shield augs from disk."""
    from inventory_parser.slot2_augs import raidloot as rl

    monkeypatch.setattr(rl, "appdata_dir", lambda: tmp_path)
    monkeypatch.setattr(
        "inventory_parser.slot2_augs.eqresource_search.fetch_eqresource_catalog",
        lambda profile, **_kwargs: _stub_eqr_catalog(profile),
    )

    shields = parse_shield_html(SHIELD_FIXTURE.read_text(encoding="utf-8"), "dex")
    disk = {
        "shield": {
            "fetched_at": "2026-01-01T00:00:00+00:00",
            "url": SHIELD_AUG_URL,
            "augs": [_candidate_to_dict(a) for a in shields],
        }
    }
    rl.cache_path().write_text(json.dumps(disk), encoding="utf-8")

    loads = {"n": 0}
    real_load = rl._load_cache

    def load_once_cold():
        loads["n"] += 1
        if loads["n"] == 1:
            return {}
        return real_load()

    monkeypatch.setattr(rl, "_load_cache", load_once_cold)

    def boom(*_args, **_kwargs):
        raise OSError("network down")

    monkeypatch.setattr(rl, "_http_get", boom)

    cat = fetch_catalog("dex")
    assert any(a.item_id == 175179 and a.shield_only for a in cat.augs)
    assert cat.warning and "using cached shield" in cat.warning.casefold()
