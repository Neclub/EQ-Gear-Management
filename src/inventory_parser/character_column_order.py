"""Persist and apply user-defined team column order."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from inventory_parser.achievement_files import parse_achievements_filename
from inventory_parser.team_report import CharacterGear, TeamGearReport, build_team_report
from inventory_parser.missing_spells import discover_persona_bindings, persona_key, split_input_paths
from inventory_parser.unmade_gear import UnmadeGearEntry

T = TypeVar("T")


@dataclass(frozen=True)
class ColumnRosterEntry:
    """One gear column persona shown in the GUI roster."""

    persona_key: str
    display_name: str
    character: str
    server: str
    class_abbr: str | None = None


def settings_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".local" / "share"
    return base / "Inventory Parser" / "settings.json"


def load_settings() -> dict:
    path = settings_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_character_column_order(order: list[str]) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = load_settings()
    settings["character_column_order"] = order
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def saved_character_column_order() -> list[str]:
    raw = load_settings().get("character_column_order", [])
    if not isinstance(raw, list):
        return []
    return [str(key) for key in raw if key]


def order_by_persona_keys(items: list[T], order: list[str], *, key_fn) -> list[T]:
    """Return items sorted by saved order, then default order for unknown keys."""
    by_key = {key_fn(item): item for item in items}
    ordered: list[T] = []
    seen: set[str] = set()
    for key in order:
        item = by_key.get(key)
        if item is not None and key not in seen:
            ordered.append(item)
            seen.add(key)
    for item in items:
        key = key_fn(item)
        if key not in seen:
            ordered.append(item)
            seen.add(key)
    return ordered


def order_roster_entries(
    entries: list[ColumnRosterEntry],
    saved_order: list[str],
) -> list[ColumnRosterEntry]:
    return order_by_persona_keys(
        entries,
        saved_order,
        key_fn=lambda entry: entry.persona_key,
    )


def build_column_roster(
    file_paths: list[str | Path],
    saved_order: list[str] | None = None,
) -> list[ColumnRosterEntry]:
    """Build gear-column roster entries from the current input file list."""
    paths = [Path(p) for p in file_paths]
    inventory_paths, spell_paths, _achievement_paths = split_input_paths(paths)
    if not inventory_paths:
        return []

    report = build_team_report(inventory_paths, spell_paths=spell_paths or None)
    entries = [
        ColumnRosterEntry(
            persona_key=character.persona_key,
            display_name=character.display_name,
            character=character.character,
            server=character.server,
            class_abbr=character.class_abbr,
        )
        for character in report.characters
    ]
    return order_roster_entries(entries, saved_order or [])


def apply_character_column_order(
    team: TeamGearReport,
    order: list[str] | None,
) -> None:
    """Reorder team gear and spell personas for export columns."""
    if not order:
        return
    team.characters = order_by_persona_keys(
        team.characters,
        order,
        key_fn=lambda row: row.persona_key,
    )
    team.spell_characters = order_by_persona_keys(
        team.spell_characters,
        order,
        key_fn=lambda row: row.persona_key,
    )


def reorder_unmade_entries(
    entries: list[UnmadeGearEntry],
    team: TeamGearReport,
    order: list[str] | None,
) -> list[UnmadeGearEntry]:
    if not order:
        return entries
    rank_by_display = {
        character.display_name: index
        for index, character in enumerate(team.characters)
    }
    return sorted(
        entries,
        key=lambda row: (
            rank_by_display.get(row.display_name, len(rank_by_display)),
            row.expansion.casefold(),
            row.material.casefold(),
            row.item_name.casefold(),
            row.bag_location.casefold(),
        ),
    )


def _char_server_key(character: str, server: str) -> tuple[str, str]:
    return character.casefold(), server.casefold()


def paths_still_needed(
    remaining: list[ColumnRosterEntry],
    file_paths: list[str | Path],
) -> set[str]:
    """Resolve which input files are still required for the remaining roster."""
    paths = [Path(p).resolve() for p in file_paths]
    inventory_paths, spell_paths, achievement_paths = split_input_paths(paths)
    if not remaining:
        return set()

    remaining_keys = {entry.persona_key for entry in remaining}
    remaining_char_servers = {
        _char_server_key(entry.character, entry.server) for entry in remaining
    }
    needed: set[str] = set()

    discovery = discover_persona_bindings(
        inventory_paths,
        spell_paths=spell_paths or None,
    )
    for binding in discovery.bindings:
        binding_key = persona_key(binding.character, binding.server, binding.class_abbr)
        char_server = _char_server_key(binding.character, binding.server)
        if binding_key in remaining_keys:
            needed.add(str(binding.inventory_path.resolve()))
            if binding.spell_path is not None:
                needed.add(str(binding.spell_path.resolve()))
        elif char_server in remaining_char_servers:
            if binding.spell_path is not None:
                needed.add(str(binding.spell_path.resolve()))
            if binding.inventory_path is not None and char_server in remaining_char_servers:
                needed.add(str(binding.inventory_path.resolve()))

    for achievement_path in achievement_paths:
        parsed = parse_achievements_filename(achievement_path)
        if parsed is None:
            continue
        character, server = parsed
        if _char_server_key(character, server) in remaining_char_servers:
            needed.add(str(achievement_path.resolve()))

    return needed


def paths_for_roster_removal(
    removing: list[ColumnRosterEntry],
    roster: list[ColumnRosterEntry],
    file_paths: list[str | Path],
) -> set[str]:
    """Paths that can be dropped after removing roster entries."""
    removing_keys = {entry.persona_key for entry in removing}
    remaining = [entry for entry in roster if entry.persona_key not in removing_keys]
    all_paths = {str(Path(path).resolve()) for path in file_paths}
    return all_paths - paths_still_needed(remaining, file_paths)
