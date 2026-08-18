"""Assemble all export data shared by Excel and HTML writers."""

from __future__ import annotations

import gc
from collections.abc import Callable
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
from inventory_parser.rune_inventory import RuneInventoryReport, build_rune_inventory_report
from inventory_parser.unmade_gear import UnmadeGearEntry, build_unmade_gear_report
from inventory_parser.useful_spells import (
    MissingUsefulSpellsReport,
    build_missing_useful_spells_report,
)
from inventory_parser.raid_bis.build import RaidBisExport, build_raid_bis_export
from inventory_parser.slot2_augs.build import Slot2Export, build_slot2_export
from inventory_parser.slot2_augs.chest_class import apply_resolved_classes_to_team
from inventory_parser.slot2_augs.eqresource_gear_tier import apply_resolved_gear_tiers_to_team


@dataclass
class ExportBundle:
    team: TeamGearReport
    spell_report: SpellRuneReport | None = None
    missing_useful_report: MissingUsefulSpellsReport | None = None
    achievement_report: AchievementReport | None = None
    unmade_entries: list[UnmadeGearEntry] = field(default_factory=list)
    rune_inventory_report: RuneInventoryReport | None = None
    warnings: list[str] = field(default_factory=list)
    slot_filter: SlotFilter = "all"
    slot2: Slot2Export | None = None
    raid_bis: RaidBisExport | None = None


def release_export_memory() -> None:
    """Drop large export allocations and encourage the GC to reclaim memory."""
    gc.collect()


def build_export_bundle(
    input_paths: list[Path],
    *,
    slot_filter: SlotFilter = "all",
    include_spells: bool = True,
    include_achievements: bool = True,
    include_slot2: bool = True,
    include_raid_bis: bool = False,
    include_anniversary: bool = False,
    session_weights: dict[str, float] | None = None,
    on_progress: Callable[[dict], None] | None = None,
    character_column_order: list[str] | None = None,
    **slot2_kwargs,
) -> ExportBundle:
    """Parse inputs and build reports for Excel/HTML export."""
    inventory_paths, spell_file_paths, achievement_file_paths = split_input_paths(input_paths)
    if not inventory_paths:
        raise ValueError(
            "No inventory files were provided. Add *-Inventory.txt files."
        )

    report = build_team_report(inventory_paths, spell_paths=spell_file_paths)
    if not report.characters:
        raise ValueError("No inventory files were parsed successfully.")

    fetch_chest_class = slot2_kwargs.get("fetch_chest_class", True)
    chest_class_overrides = slot2_kwargs.get("chest_class_overrides")
    apply_resolved_classes_to_team(
        report,
        overrides=chest_class_overrides,
        allow_network=bool(fetch_chest_class),
    )

    fetch_eqr_gear_tiers = slot2_kwargs.pop("fetch_eqr_gear_tiers", True)
    eqr_gear_tier_html = slot2_kwargs.pop("eqr_gear_tier_html", None)
    apply_resolved_gear_tiers_to_team(
        report,
        html_overrides=eqr_gear_tier_html,
        allow_network=bool(fetch_eqr_gear_tiers),
    )

    apply_character_column_order(report, character_column_order)

    warnings = list(report.warnings)
    spell_report = None
    missing_useful_report = None
    if include_spells:
        spell_report = build_spell_rune_report(
            report,
            inventory_paths=inventory_paths,
            extra_spell_paths=spell_file_paths,
        )
        if spell_report is not None:
            warnings.extend(spell_report.warnings)
        missing_useful_report = build_missing_useful_spells_report(
            report,
            inventory_paths=inventory_paths,
            extra_spell_paths=spell_file_paths,
        )
        if missing_useful_report is not None:
            warnings.extend(missing_useful_report.warnings)

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
    rune_inventory_report = build_rune_inventory_report(report)

    raid_bis_overrides = slot2_kwargs.pop("raid_bis_html_overrides", None)
    raid_bis_item_html = slot2_kwargs.pop("raid_bis_item_html", None)
    raid_bis_allow_network = slot2_kwargs.pop("raid_bis_allow_network", True)
    raid_bis_hydrate = slot2_kwargs.pop("raid_bis_hydrate", True)
    raid_bis_embed_icons = slot2_kwargs.pop("raid_bis_embed_icons", True)

    slot2 = None
    if include_slot2:
        slot2 = build_slot2_export(
            report,
            include_anniversary=include_anniversary,
            session_weights=session_weights,
            on_progress=on_progress,
            **slot2_kwargs,
        )
        warnings.extend(slot2.warnings)

    raid_bis = None
    if include_raid_bis:
        raid_bis = build_raid_bis_export(
            report,
            on_progress=on_progress,
            allow_network=bool(raid_bis_allow_network),
            html_overrides=raid_bis_overrides,
            item_html_by_id=raid_bis_item_html,
            hydrate=bool(raid_bis_hydrate),
            embed_icons=bool(raid_bis_embed_icons),
        )
        warnings.extend(raid_bis.warnings)

    return ExportBundle(
        team=report,
        spell_report=spell_report,
        missing_useful_report=missing_useful_report,
        achievement_report=achievement_report,
        unmade_entries=unmade_entries,
        rune_inventory_report=rune_inventory_report,
        warnings=warnings,
        slot_filter=slot_filter,
        slot2=slot2,
        raid_bis=raid_bis,
    )
