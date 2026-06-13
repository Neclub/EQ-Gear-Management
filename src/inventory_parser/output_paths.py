"""Default team inventory export file names."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from inventory_parser.team_report import TeamGearReport
from inventory_parser.eq_servers import server_display_name, server_slug_from_eqlog_filename
from inventory_parser.missing_spells import (
    is_inventory_file,
    is_missing_spells_file,
    parse_missing_spells_filename,
)
from inventory_parser.parser import parse_character_from_filename

TEAM_INVENTORY_BASENAME = "Team Inventory"
LEGACY_CREW_INVENTORY_BASENAME = "Crew Inventory"
TEAM_INVENTORY_SUFFIX = ".xlsx"
TEAM_INVENTORY_HTML_SUFFIX = ".html"


def team_inventory_filename(prefix: str | None = None) -> str:
    """Return export workbook filename, e.g. ``Deflub_Team Inventory.xlsx``."""
    if prefix:
        return f"{prefix}_{TEAM_INVENTORY_BASENAME}{TEAM_INVENTORY_SUFFIX}"
    return f"{TEAM_INVENTORY_BASENAME}{TEAM_INVENTORY_SUFFIX}"


def team_inventory_html_filename(prefix: str | None = None) -> str:
    """Return export HTML filename, e.g. ``Deflub_Team Inventory.html``."""
    if prefix:
        return f"{prefix}_{TEAM_INVENTORY_BASENAME}{TEAM_INVENTORY_HTML_SUFFIX}"
    return f"{TEAM_INVENTORY_BASENAME}{TEAM_INVENTORY_HTML_SUFFIX}"


def team_inventory_path(directory: Path, prefix: str | None = None) -> Path:
    return directory / team_inventory_filename(prefix)


def team_inventory_html_path(directory: Path, prefix: str | None = None) -> Path:
    return directory / team_inventory_html_filename(prefix)


def html_path_for_workbook(workbook_path: Path | str) -> Path:
    """Sibling HTML path for an Excel export (same stem, ``.html`` extension)."""
    path = Path(workbook_path)
    return path.with_suffix(TEAM_INVENTORY_HTML_SUFFIX)


def _server_slug_from_path(path: Path) -> str | None:
    if is_inventory_file(path):
        _, server = parse_character_from_filename(path)
        return server or None
    if is_missing_spells_file(path):
        parsed = parse_missing_spells_filename(path)
        return parsed[1] if parsed else None
    slug = server_slug_from_eqlog_filename(path)
    return slug or None


def _collect_server_slugs(paths: Iterable[Path | str]) -> dict[str, str]:
    """Map casefolded slug -> slug as it appears in a log filename."""
    servers: dict[str, str] = {}
    scan_dirs: set[Path] = set()

    for raw in paths:
        path = Path(raw)
        slug = _server_slug_from_path(path)
        if slug:
            servers[slug.casefold()] = slug
        if path.is_file():
            scan_dirs.add(path.parent)

    for folder in scan_dirs:
        if not folder.is_dir():
            continue
        for eqlog in folder.glob("eqlog_*.txt"):
            slug = server_slug_from_eqlog_filename(eqlog)
            if slug:
                servers[slug.casefold()] = slug

    return servers


def server_slug_from_input_paths(paths: Iterable[Path | str]) -> str | None:
    """Return the server slug when all inventory, spell, and eqlog paths agree."""
    servers = _collect_server_slugs(paths)
    if len(servers) == 1:
        return next(iter(servers.values()))
    return None


def server_slug_from_inventory_paths(paths: Iterable[Path | str]) -> str | None:
    """Backward-compatible alias for :func:`server_slug_from_input_paths`."""
    return server_slug_from_input_paths(paths)


def server_slug_from_report(report: TeamGearReport) -> str | None:
    servers = {c.server for c in report.characters if c.server}
    if len(servers) == 1:
        return next(iter(servers))
    return None


def _collect_inventory_characters(paths: Iterable[Path | str]) -> dict[str, str]:
    """Map casefolded character name -> name as it appears in a log filename."""
    characters: dict[str, str] = {}
    for raw in paths:
        path = Path(raw)
        if is_inventory_file(path):
            character, _ = parse_character_from_filename(path)
            if character:
                characters[character.casefold()] = character
    return characters


def default_export_prefix_from_input_paths(paths: Iterable[Path | str]) -> str | None:
    """
    Return the export filename prefix for the selected inputs.

    One inventory character -> that character's name; otherwise the shared server
    display name when all paths agree on server.
    """
    characters = _collect_inventory_characters(paths)
    if len(characters) == 1:
        return next(iter(characters.values()))
    slug = server_slug_from_input_paths(paths)
    return server_display_name(slug) if slug else None


def default_export_prefix_from_report(report: TeamGearReport) -> str | None:
    """Like :func:`default_export_prefix_from_input_paths`, but from a built report."""
    characters = {c.character for c in report.characters if c.character}
    if len(characters) == 1:
        return next(iter(characters))
    slug = server_slug_from_report(report)
    return server_display_name(slug) if slug else None


def is_auto_team_inventory_path(path: str | Path) -> bool:
    """True when the path looks like an app-generated default export name."""
    stem = Path(path).stem
    for basename in (TEAM_INVENTORY_BASENAME, LEGACY_CREW_INVENTORY_BASENAME):
        if stem == basename or stem.endswith(f"_{basename}"):
            return True
    return False
