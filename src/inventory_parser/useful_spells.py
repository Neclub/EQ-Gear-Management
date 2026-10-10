"""Curated useful spells intersected with MissingSpells dumps."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from inventory_parser.missing_spells import (
    MissingSpellLine,
    discover_missing_spells_for_inventories,
    is_missing_rank_iii,
    current_rank_from_log,
    parse_missing_spells_file,
    spell_path_for_persona,
    strip_spell_rank,
)
from inventory_parser.package_data import read_data_text
from inventory_parser.spell_catalog import (
    SpellCatalog,
    SpellCatalogEntry,
    eqresource_spell_url,
    load_spell_catalog,
    lookup_spell_id,
)
from inventory_parser.team_report import TeamGearReport

_CATALOG_NAME = "useful_spells.json"

RACCOO_USEFUL_SPELLS_CREDIT_TEXT = 'Based on "SOR - Raccoo\'s list of useful spells"'
RACCOO_USEFUL_SPELLS_URL = (
    "https://docs.google.com/spreadsheets/d/1ZqUFZ-WTZvfcBfwu5g6GGEQroEwNLSfK1LMOdMHVHcA/htmlview"
)

# Trailing roman / arabic rank token (Dichotemic Fury VI, Reciprocal Rage 6, etc.)
_TRAILING_RANK_TOKEN_RE = re.compile(
    r"\s+(?:X{0,3}(?:IX|IV|V?I{0,3})|\d+)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class UsefulSpell:
    name: str
    level: int | None
    expansion: str = ""
    highest_rk: str = ""
    comments: str = ""


@dataclass(frozen=True)
class MissingUsefulSpell:
    persona_key: str
    display_name: str
    character: str
    level: int
    expansion: str
    spell_name: str
    current_rank: str
    comments: str
    eqresource_url: str = ""


@dataclass
class MissingUsefulSpellsReport:
    persona_keys: list[str]
    entries: list[MissingUsefulSpell] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _spell_personas(team: TeamGearReport) -> list:
    if team.spell_characters:
        return team.spell_characters
    return team.characters


def _parse_catalog(data: dict[str, Any]) -> dict[str, list[UsefulSpell]]:
    raw = data.get("spells_by_class", {})
    by_class: dict[str, list[UsefulSpell]] = {}
    if not isinstance(raw, dict):
        return by_class
    for class_abbr, spells in raw.items():
        if not isinstance(spells, list):
            continue
        parsed: list[UsefulSpell] = []
        for entry in spells:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            if not name:
                continue
            level_raw = entry.get("level")
            level: int | None
            try:
                level = int(level_raw) if level_raw is not None else None
            except (TypeError, ValueError):
                level = None
            parsed.append(
                UsefulSpell(
                    name=name,
                    level=level,
                    expansion=str(entry.get("expansion", "") or "").strip(),
                    highest_rk=str(entry.get("highest_rk", "") or "").strip(),
                    comments=str(entry.get("comments", "") or "").strip(),
                )
            )
        by_class[str(class_abbr).upper()] = parsed
    return by_class


@lru_cache(maxsize=1)
def load_useful_spells() -> dict[str, list[UsefulSpell]]:
    """Return useful spells keyed by class abbreviation (SHD, PAL, …)."""
    text = read_data_text(_CATALOG_NAME)
    return _parse_catalog(json.loads(text))


def _highest_rk_is_numeric(highest_rk: str) -> bool:
    return bool(re.fullmatch(r"\d+", highest_rk.strip()))


def _normalize_spell_name(name: str) -> str:
    """Comparable spell name: rank suffix off, punctuation and Disc folded."""
    text = strip_spell_rank(name).casefold()
    text = re.sub(r"\bdiscipline\b", "disc", text)
    text = text.replace("'", "").replace("\u2019", "").replace("\u2032", "")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace(" of of ", " of ")


def _split_line_token(name: str) -> tuple[str, str]:
    """Split a trailing spell-line numeral (``IX``, ``6``) from a normalized name."""
    match = _TRAILING_RANK_TOKEN_RE.search(name)
    if match is None:
        return name, ""
    token = match.group(0).strip().casefold()
    if not token:
        return name, ""
    return name[: match.start()].strip(), token


def _edit_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    prev = list(range(len(right) + 1))
    for i, left_char in enumerate(left, 1):
        current = [i]
        for j, right_char in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    prev[j] + 1,
                    prev[j - 1] + (left_char != right_char),
                )
            )
        prev = current
    return prev[-1]


@dataclass(frozen=True)
class _ResolvedSpell:
    """Spell identity used to accept a MissingSpells line."""

    name: str
    level: int | None
    line_token: str
    from_catalog: bool


def _catalog_name_hit(useful_name: str, entry_name: str) -> bool:
    """True when the catalog name is the curated name, or that name plus one line numeral."""
    if entry_name == useful_name:
        return True
    useful_token = _split_line_token(useful_name)[1]
    entry_stem, entry_token = _split_line_token(entry_name)
    return not useful_token and bool(entry_token) and entry_stem == useful_name


def _typo_catalog_hit(
    useful_name: str,
    level: int,
    entries: list[SpellCatalogEntry],
) -> SpellCatalogEntry | None:
    """Unique same-level catalog spell with the same line numeral and a small edit distance."""
    useful_stem, useful_token = _split_line_token(useful_name)
    scored: list[tuple[int, SpellCatalogEntry]] = []
    for entry in entries:
        if entry.level != level:
            continue
        entry_name = _normalize_spell_name(entry.name)
        entry_stem, entry_token = _split_line_token(entry_name)
        if entry_token != useful_token:
            continue
        scored.append((_edit_distance(useful_stem, entry_stem), entry))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    best_distance, best_entry = scored[0]
    if best_distance <= 0 or best_distance > 3:
        return None
    next_distance = scored[1][0] if len(scored) > 1 else best_distance + 4
    if next_distance - best_distance < 4:
        return None
    return best_entry


def _resolve_useful_spell(
    useful: UsefulSpell,
    class_abbr: str | None,
    spell_catalog: SpellCatalog | None,
) -> _ResolvedSpell:
    """Map a curated row onto the in-game spell name and level when the catalog can."""
    useful_name = _normalize_spell_name(useful.name)
    line_token = _split_line_token(useful_name)[1]
    listed = _ResolvedSpell(
        name=useful_name,
        level=useful.level,
        line_token=line_token,
        from_catalog=False,
    )
    if (
        spell_catalog is None
        or not class_abbr
        or useful.level is None
        or not 121 <= useful.level <= 130
    ):
        return listed

    entries = list(spell_catalog.spells_by_class.get(class_abbr.upper(), {}).values())
    exact = [
        entry
        for entry in entries
        if _catalog_name_hit(useful_name, _normalize_spell_name(entry.name))
    ]
    chosen: SpellCatalogEntry | None
    if len(exact) == 1:
        chosen = exact[0]
    elif exact:
        chosen = None
    else:
        chosen = _typo_catalog_hit(useful_name, useful.level, entries)
    if chosen is None:
        return listed
    canonical = _normalize_spell_name(chosen.name)
    return _ResolvedSpell(
        name=canonical,
        level=chosen.level,
        line_token=_split_line_token(canonical)[1],
        from_catalog=True,
    )


def useful_matches_missing(useful: UsefulSpell, missing_name: str) -> bool:
    """True when a MissingSpells line's name corresponds to a curated useful spell.

    Level and catalog identity are applied by ``_line_matches_useful``.
    """
    missing_name_key = _normalize_spell_name(missing_name)
    useful_key = _normalize_spell_name(useful.name)
    if missing_name_key == useful_key:
        return True
    if _highest_rk_is_numeric(useful.highest_rk):
        stem, token = _split_line_token(missing_name_key)
        if token and stem == useful_key:
            return True
    return False


def _line_matches_useful(
    useful: UsefulSpell,
    line: MissingSpellLine,
    resolved: _ResolvedSpell,
) -> bool:
    """True when this MissingSpells line is the resolved useful spell."""
    log_name = _normalize_spell_name(line.name)
    log_stem, log_token = _split_line_token(log_name)
    names_equal = log_name == resolved.name
    extra_rank = (
        not resolved.from_catalog
        and _highest_rk_is_numeric(useful.highest_rk)
        and bool(log_token)
        and log_stem == resolved.name
    )
    if not names_equal and not extra_rank:
        return False
    if resolved.level is None or line.level == resolved.level:
        return True
    # Below the 121–130 catalog, a name that already includes its line numeral
    # may sit at the log's level when the curated sheet's level is off.
    return (
        names_equal
        and not resolved.from_catalog
        and bool(resolved.line_token)
        and useful.level is not None
        and useful.level < 121
    )


def _rank_preference(spell_name: str) -> int:
    """Higher is better when choosing among duplicate missing lines."""
    if is_missing_rank_iii(spell_name):
        return 3
    if re.search(r"Rk\.?\s*II\b", spell_name, re.IGNORECASE):
        return 2
    # Trailing roman / number after base name
    token = _TRAILING_RANK_TOKEN_RE.search(strip_spell_rank(spell_name))
    if token:
        raw = token.group(0).strip().upper()
        roman = {
            "I": 1,
            "II": 2,
            "III": 3,
            "IV": 4,
            "V": 5,
            "VI": 6,
            "VII": 7,
            "VIII": 8,
            "IX": 9,
            "X": 10,
            "XI": 11,
            "XII": 12,
        }
        if raw in roman:
            return roman[raw]
        if raw.isdigit():
            return int(raw)
    return 1


def _pick_best_missing(
    useful: UsefulSpell,
    candidates: list[MissingSpellLine],
    *,
    class_abbr: str | None,
    spell_catalog: SpellCatalog | None,
) -> MissingSpellLine | None:
    resolved = _resolve_useful_spell(useful, class_abbr, spell_catalog)
    matches = [
        line for line in candidates if _line_matches_useful(useful, line, resolved)
    ]
    if not matches:
        return None
    return max(matches, key=lambda line: (_rank_preference(line.name), line.level))


def build_missing_useful_spells_report(
    team: TeamGearReport,
    spell_paths: dict[str, Path] | None = None,
    *,
    inventory_paths: list[Path] | None = None,
    extra_spell_paths: list[Path] | None = None,
    discovery_warnings: list[str] | None = None,
    useful_by_class: dict[str, list[UsefulSpell]] | None = None,
) -> MissingUsefulSpellsReport | None:
    """
    Intersect each persona's MissingSpells dump with the curated useful list.

    Includes all levels (not limited to the 121–130 rune band).
    """
    personas = _spell_personas(team)
    warnings: list[str] = list(discovery_warnings or [])
    if spell_paths is None:
        inv_paths = inventory_paths or [Path(c.filepath) for c in personas]
        discovery = discover_missing_spells_for_inventories(
            inv_paths,
            extra_spell_paths=extra_spell_paths,
        )
        spell_paths = discovery.paths
        warnings.extend(discovery.warnings)

    if not spell_paths:
        return None

    catalog = useful_by_class if useful_by_class is not None else load_useful_spells()
    spell_catalog = load_spell_catalog()
    persona_order = [c.persona_key for c in personas]
    report = MissingUsefulSpellsReport(persona_keys=persona_order, warnings=warnings)

    for char_gear in personas:
        pk = char_gear.persona_key
        class_abbr = (char_gear.class_abbr or "").upper() or None
        spell_path = spell_path_for_persona(
            char_gear.character,
            char_gear.server,
            char_gear.class_abbr,
            spell_paths,
        )
        if spell_path is None:
            continue
        if not class_abbr:
            report.warnings.append(
                f"No class for {char_gear.display_name}; skipping useful-spell check"
            )
            continue
        useful_list = catalog.get(class_abbr)
        if not useful_list:
            report.warnings.append(
                f"No useful-spell list for class {class_abbr} ({char_gear.display_name})"
            )
            continue

        missing_lines = parse_missing_spells_file(spell_path)
        for useful in useful_list:
            best = _pick_best_missing(
                useful,
                missing_lines,
                class_abbr=class_abbr,
                spell_catalog=spell_catalog,
            )
            if best is None:
                continue
            level = best.level
            spell_id = lookup_spell_id(
                class_abbr,
                level,
                best.name,
                catalog=spell_catalog,
            )
            report.entries.append(
                MissingUsefulSpell(
                    persona_key=pk,
                    display_name=char_gear.display_name,
                    character=char_gear.character,
                    level=level,
                    expansion=useful.expansion,
                    spell_name=strip_spell_rank(best.name),
                    current_rank=current_rank_from_log(best.name),
                    comments=useful.comments,
                    eqresource_url=eqresource_spell_url(
                        spell_id,
                        best.name,
                        class_abbr=class_abbr,
                        level=level,
                    ),
                )
            )

    report.entries.sort(
        key=lambda e: (
            e.persona_key.casefold(),
            -(e.level),
            e.spell_name.casefold(),
        )
    )
    return report
