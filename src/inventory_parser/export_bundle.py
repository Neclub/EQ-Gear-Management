"""Assemble all export data shared by Excel and HTML writers."""

from __future__ import annotations

import gc
from dataclasses import dataclass, field
from pathlib import Path

from inventory_parser.achievement_report import AchievementReport, build_achievement_report
from inventory_parser.character_column_order import (
    apply_character_column_order,
    reorder_unmade_entries,
)
from inventory_parser.team_report import TeamGearReport, build_team_report
from inventory_parser.missing_spells import split_input_paths
from inventory_parser.slots import SlotFilter
from inventory_parser.spell_report import SpellRuneReport, build_spell_rune_report
from inventory_parser.unmade_gear import UnmadeGearEntry, build_unmade_gear_report


@dataclass
class ExportBundle:
    team: TeamGearReport
    spell_report: SpellRuneReport | None = None
    achievement_report: AchievementReport | None = None
    unmade_entries: list[UnmadeGearEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    slot_filter: SlotFilter = "all"


def release_export_memory() -> None:
    """Drop large export allocations and encourage the GC to reclaim memory."""
    gc.collect()


def build_export_bundle(
    input_paths: list[Path],
    *,
    slot_filter: SlotFilter = "all",
    include_spells: bool = True,
    include_achievements: bool = True,
    character_column_order: list[str] | None = None,
) -> ExportBundle:
    """Parse inputs and build reports for Excel/HTML export."""
    inventory_paths, spell_file_paths, achievement_file_paths = split_input_paths(input_paths)
    if not inventory_paths:
        raise ValueError(
            "No inventory files were provided. Add *-Inventory.txt dumps."
        )

    report = build_team_report(inventory_paths, spell_paths=spell_file_paths)
    if not report.characters:
        raise ValueError("No inventory files were parsed successfully.")

    apply_character_column_order(report, character_column_order)

    warnings = list(report.warnings)
    spell_report = None
    if include_spells:
        spell_report = build_spell_rune_report(
            report,
            inventory_paths=inventory_paths,
            extra_spell_paths=spell_file_paths,
        )
        if spell_report is not None:
            warnings.extend(spell_report.warnings)

    achievement_report = None
    if include_achievements:
        achievement_report = build_achievement_report(
            report,
            inventory_paths=inventory_paths,
            extra_achievement_paths=achievement_file_paths,
        )
        if achievement_report is not None:
            warnings.extend(achievement_report.warnings)

    unmade_entries = reorder_unmade_entries(
        build_unmade_gear_report(report),
        report,
        character_column_order,
    )
    return ExportBundle(
        team=report,
        spell_report=spell_report,
        achievement_report=achievement_report,
        unmade_entries=unmade_entries,
        warnings=warnings,
        slot_filter=slot_filter,
    )
