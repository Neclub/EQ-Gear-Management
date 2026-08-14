from __future__ import annotations

from pathlib import Path

from inventory_parser.spell_catalog import (
    load_spell_catalog,
    lookup_expansion,
    lookup_expansion_label,
)
from inventory_parser.spell_scrape import parse_spell_search_html

WIZ_HTML = Path(__file__).resolve().parent / "fixtures" / "eqresource_spellsearch_wiz.html"


def test_parse_spell_search_html_rk3_only() -> None:
    html = WIZ_HTML.read_text(encoding="utf-8")
    spells = parse_spell_search_html(html)
    assert spells
    assert all(121 <= int(s["level"]) <= 130 for s in spells)
    assert all("Rk. III" in str(s["name"]) for s in spells)
    assert all(s["expansion"] in ("Laurion's Song", "The Outer Brood", "Shattering of Ro") for s in spells)

    by_name = {str(s["name"]): s for s in spells}
    assert by_name["Cloudburst Lightningstrike Rk. III"]["expansion"] == "Laurion's Song"
    assert by_name["Chromospheric Vortex Rk. III"]["expansion"] == "The Outer Brood"
    assert by_name["Aegis of Feish Rk. III"]["expansion"] == "Shattering of Ro"


def test_lookup_expansion_for_wizard_missing_spell() -> None:
    catalog = load_spell_catalog()
    assert (
        lookup_expansion("WIZ", 122, "Cloudburst Lightningstrike Rk. III", catalog=catalog)
        == "Laurion's Song"
    )
    assert (
        lookup_expansion_label("WIZ", 123, "Chromospheric Vortex Rk. III", catalog=catalog)
        == "The Outer Brood (2024)"
    )


def test_lookup_expansion_unknown_returns_none() -> None:
    catalog = load_spell_catalog()
    assert lookup_expansion("WIZ", 121, "Not A Real Spell Rk. III", catalog=catalog) is None
    assert lookup_expansion_label("WIZ", 121, "Not A Real Spell Rk. III", catalog=catalog) == ""


def test_lookup_expansion_requires_class() -> None:
    assert lookup_expansion(None, 126, "Committal Rk. III") is None
