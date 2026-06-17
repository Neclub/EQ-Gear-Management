"""Lookup spell expansion from the bundled EQ Resource catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from inventory_parser.achievement_parser import format_expansion_label
from inventory_parser.missing_spells import strip_spell_rank
from inventory_parser.package_data import read_data_text

_CATALOG_NAME = "spell_expansions_121_130.json"


@dataclass(frozen=True)
class SpellCatalogEntry:
    level: int
    name: str
    expansion: str
    spell_id: int


@dataclass(frozen=True)
class SpellCatalog:
    spells_by_class: dict[str, dict[str, SpellCatalogEntry]]

    def lookup(self, class_abbr: str | None, level: int, spell_name: str) -> SpellCatalogEntry | None:
        if not class_abbr:
            return None
        class_spells = self.spells_by_class.get(class_abbr.upper())
        if class_spells is None:
            return None
        key = f"{level}|{strip_spell_rank(spell_name).casefold()}"
        return class_spells.get(key)



def _parse_catalog(data: dict[str, Any]) -> SpellCatalog:
    raw_spells = data.get("spells", {})
    spells_by_class: dict[str, dict[str, SpellCatalogEntry]] = {}
    for class_abbr, class_spells in raw_spells.items():
        if not isinstance(class_spells, dict):
            continue
        parsed: dict[str, SpellCatalogEntry] = {}
        for key, entry in class_spells.items():
            if not isinstance(entry, dict):
                continue
            parsed[str(key)] = SpellCatalogEntry(
                level=int(entry["level"]),
                name=str(entry["name"]),
                expansion=str(entry["expansion"]),
                spell_id=int(entry["spell_id"]),
            )
        spells_by_class[str(class_abbr).upper()] = parsed
    return SpellCatalog(spells_by_class=spells_by_class)


@lru_cache(maxsize=1)
def load_spell_catalog() -> SpellCatalog:
    text = read_data_text(_CATALOG_NAME)
    return _parse_catalog(json.loads(text))


def lookup_expansion(
    class_abbr: str | None,
    level: int,
    spell_name: str,
    *,
    catalog: SpellCatalog | None = None,
) -> str | None:
    """Return the canonical expansion name for a spell, if known."""
    cat = catalog or load_spell_catalog()
    entry = cat.lookup(class_abbr, level, spell_name)
    if entry is None:
        return None
    return entry.expansion


def lookup_expansion_label(
    class_abbr: str | None,
    level: int,
    spell_name: str,
    *,
    catalog: SpellCatalog | None = None,
) -> str:
    """Return a display label for filters; blank when unknown."""
    expansion = lookup_expansion(class_abbr, level, spell_name, catalog=catalog)
    if expansion is None:
        return ""
    return format_expansion_label(expansion)
