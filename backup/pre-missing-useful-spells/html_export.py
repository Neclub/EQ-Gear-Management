"""Export team reports to a self-contained interactive HTML file."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from inventory_parser import __version__
from inventory_parser.achievement_parser import (
    EVERQUEST_BASE_LABEL,
    EXPANSIONS_NEWEST_FIRST,
    format_expansion_label,
)
from inventory_parser.team_report import CharacterGear, TeamGearReport
from inventory_parser.excel_export import (
    ACHIEVEMENT_SUMMARY_SHEET_NAME,
    GEAR_T_LEVEL_SHEET_NAME,
    MISSING_COLLECTIONS_SHEET_NAME,
    MISSING_SPELLS_SHEET_NAME,
    RAID_ACHIEVEMENTS_SHEET_NAME,
    RUNE_INVENTORY_SHEET_NAME,
    UNMADE_GEAR_SHEET_NAME,
)
from inventory_parser.excel_theme import GEAR_SET_FILLS, SPELL_TIER_COLORS, build_gear_legend, build_tier_code_colors
from inventory_parser.export_bundle import ExportBundle
from inventory_parser.items import EQRESOURCE_ITEM_URL, EquippedItem
from inventory_parser.rune_inventory import RuneInventoryReport
from inventory_parser.output_paths import default_export_prefix_from_report
from inventory_parser.package_data import asset_path, read_data_text
from inventory_parser.slots import slot_visibility, slots_for_export
from inventory_parser.sor_tier import sor_gap_label
from inventory_parser.spell_runes import load_rune_config

_REPORT_JSON_MARKER = "/*__REPORT_JSON__*/"


def _slots_for_tier_sheet(report: TeamGearReport, base_slots: tuple[str, ...]) -> tuple[str, ...]:
    slots = list(base_slots)
    if "Secondary" in slots and not any("Secondary" in c.slots for c in report.characters):
        slots.remove("Secondary")
    return tuple(slots)


def _spell_characters(team: TeamGearReport, spell_report: SpellRuneReport) -> list[CharacterGear]:
    personas = team.spell_characters if team.spell_characters else team.characters
    if spell_report.persona_keys:
        by_persona = {c.persona_key: c for c in personas}
        return [by_persona[pk] for pk in spell_report.persona_keys if pk in by_persona]
    return list(personas)


def _item_url(item_id: int) -> str | None:
    if item_id > 0:
        return EQRESOURCE_ITEM_URL.format(item_id=item_id)
    return None


def _gear_item_cell(item: EquippedItem | None) -> dict | None:
    if item is None:
        return None
    tier_code = sor_gap_label(item.name, is_evolver=item.is_evolver)
    return {
        "name": item.name,
        "itemId": item.item_id,
        "url": _item_url(item.item_id),
        "tierCode": tier_code,
        "isEvolver": item.is_evolver,
    }


def _tier_cell(item: EquippedItem | None) -> dict | None:
    if item is None:
        return None
    label = sor_gap_label(item.name, is_evolver=item.is_evolver)
    if not label:
        return None
    return {"label": label, "tierCode": label}


def _gear_matrix(report: TeamGearReport, slots: tuple[str, ...], *, tier_mode: bool) -> dict:
    characters = [c.display_name for c in report.characters]
    rows: list[dict] = []
    for slot in slots:
        cells: list[dict | None] = []
        for character in report.characters:
            item = character.slots.get(slot)
            cells.append(_tier_cell(item) if tier_mode else _gear_item_cell(item))
        rows.append(
            {
                "slot": slot,
                "visibility": slot_visibility(slot),
                "cells": cells,
            }
        )
    return {"characters": characters, "rows": rows}


def _expansion_filter_order() -> list[str]:
    labels = [format_expansion_label(name) for name, _year in EXPANSIONS_NEWEST_FIRST]
    labels.append(EVERQUEST_BASE_LABEL)
    return labels


def _serialize_spell_list(spell_report: SpellRuneReport, characters: list[CharacterGear]) -> dict:
    columns = ["Character", "Level", "Rune", "Expansion", "Spell"]
    rows = [
        [
            entry.display_name,
            entry.level,
            entry.rune_tier,
            entry.expansion,
            entry.spell_name,
        ]
        for entry in spell_report.entries
    ]
    tiers_in_data = {entry.rune_tier for entry in spell_report.entries}
    tier_order = load_rune_config().tiers
    rune_options = [tier for tier in tier_order if tier in tiers_in_data]
    return {
        "columns": columns,
        "rows": rows,
        "characterColumn": 0,
        "runeColumn": 2,
        "runeOptions": rune_options,
        "expansionColumn": 3,
    }


def _serialize_missing_runes(
    spell_report: SpellRuneReport,
    characters: list[CharacterGear],
    tiers: tuple[str, ...],
) -> dict:
    blocks: list[dict] = []
    for group in spell_report.expansion_groups:
        block_rows: list[dict] = []
        for tier in tiers:
            counts = [
                spell_report.counts_by_persona.get(char.persona_key, {})
                .get(group.label, {})
                .get(tier, 0)
                for char in characters
            ]
            block_rows.append({"tier": tier, "counts": counts})
        blocks.append(
            {
                "label": group.label,
                "theme": group.turn_in_theme,
                "rows": block_rows,
            }
        )
    return {
        "characters": [c.display_name for c in characters],
        "blocks": blocks,
    }


def _serialize_rune_inventory(report: RuneInventoryReport) -> dict:
    families: list[dict] = []
    expansion_options: list[str] = []
    for family in report.families:
        family_rows: list[dict] = []
        for tier in family.tiers:
            counts = [
                family.counts.get(char.persona_key, {}).get(tier, 0)
                for char in report.characters
            ]
            family_rows.append({"tier": tier, "counts": counts})
        has_counts = any(count > 0 for row in family_rows for count in row["counts"])
        if has_counts:
            expansion_options.append(family.label)
        families.append(
            {
                "id": family.id,
                "label": family.label,
                "itemPattern": family.item_pattern,
                "rows": family_rows,
            }
        )
    return {
        "characters": [c.display_name for c in report.characters],
        "families": families,
        "expansionOptions": expansion_options,
    }


def _eq_logo_data_uri() -> str:
    data = asset_path("eq-icon.png").read_bytes()
    encoded = base64.standard_b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _serialize_table(
    columns: list[str],
    rows: list[list[object]],
    *,
    character_column: int | None = 0,
    expansion_column: int | None = None,
) -> dict:
    return {
        "columns": columns,
        "rows": rows,
        "characterColumn": character_column,
        "expansionColumn": expansion_column,
    }


def serialize_report(bundle: ExportBundle) -> dict:
    """Build JSON payload for the HTML template."""
    report = bundle.team
    base_slots = slots_for_export(bundle.slot_filter)
    tier_slots = _slots_for_tier_sheet(report, base_slots)
    sections: list[dict] = []

    sections.append(
        {
            "id": "team_gear",
            "title": "Team Gear",
            "type": "gear_matrix",
            "data": _gear_matrix(report, base_slots, tier_mode=False),
        }
    )
    sections.append(
        {
            "id": "gear_t_level",
            "title": GEAR_T_LEVEL_SHEET_NAME,
            "type": "gear_matrix",
            "data": _gear_matrix(report, tier_slots, tier_mode=True),
        }
    )

    if bundle.spell_report is not None:
        spell_chars = _spell_characters(report, bundle.spell_report)
        from inventory_parser.spell_runes import load_rune_config

        config = load_rune_config()
        sections.append(
            {
                "id": "missing_runes",
                "title": "Missing Runes",
                "type": "missing_runes",
                "data": _serialize_missing_runes(
                    bundle.spell_report,
                    spell_chars,
                    config.tiers,
                ),
            }
        )
        sections.append(
            {
                "id": "spell_list",
                "title": MISSING_SPELLS_SHEET_NAME,
                "type": "table",
                "data": _serialize_spell_list(bundle.spell_report, spell_chars),
            }
        )

    if bundle.rune_inventory_report is not None:
        sections.append(
            {
                "id": "rune_inventory",
                "title": RUNE_INVENTORY_SHEET_NAME,
                "type": "rune_inventory",
                "data": _serialize_rune_inventory(bundle.rune_inventory_report),
            }
        )

    if bundle.unmade_entries:
        sections.append(
            {
                "id": "unmade_gear",
                "title": UNMADE_GEAR_SHEET_NAME,
                "type": "table",
                "data": _serialize_table(
                    [
                        "Character",
                        "Item",
                        "Count",
                        "Bag Location",
                        "Expansion",
                        "Material",
                        "Target Slot",
                        "Equipped Tier",
                        "Notes",
                    ],
                    [
                        [
                            entry.display_name,
                            entry.item_name,
                            entry.count,
                            entry.bag_location,
                            entry.expansion,
                            entry.material,
                            entry.target_slot or "",
                            entry.equipped_tier,
                            entry.notes,
                        ]
                        for entry in bundle.unmade_entries
                    ],
                    character_column=0,
                    expansion_column=4,
                ),
            }
        )

    if bundle.achievement_report is not None:
        ach = bundle.achievement_report
        if ach.missing_collections:
            sections.append(
                {
                    "id": "missing_collections",
                    "title": MISSING_COLLECTIONS_SHEET_NAME,
                    "type": "table",
                    "data": _serialize_table(
                        [
                            "Character",
                            "Expansion",
                            "Zone",
                            "Collection",
                            "Missing Item",
                            "Progress",
                            "Char Has",
                            "Total",
                        ],
                        [
                            [
                                row.character,
                                format_expansion_label(row.expansion),
                                row.zone,
                                row.collection,
                                row.missing_item,
                                row.progress,
                                row.char_has,
                                row.total,
                            ]
                            for row in ach.missing_collections
                        ],
                        character_column=0,
                        expansion_column=1,
                    ),
                }
            )
        if ach.raid_achievements:
            sections.append(
                {
                    "id": "raid_achievements",
                    "title": RAID_ACHIEVEMENTS_SHEET_NAME,
                    "type": "table",
                    "data": _serialize_table(
                        ["Character", "Expansion", "Raid", "Objective"],
                        [
                            [
                                row.character,
                                format_expansion_label(row.expansion),
                                row.raid,
                                row.objective,
                            ]
                            for row in ach.raid_achievements
                        ],
                        character_column=0,
                        expansion_column=1,
                    ),
                }
            )
        if ach.summaries:
            sections.append(
                {
                    "id": "achievement_summary",
                    "title": ACHIEVEMENT_SUMMARY_SHEET_NAME,
                    "type": "table",
                    "data": _serialize_table(
                        [
                            "Character",
                            "Section",
                            "Completed",
                            "Incomplete",
                            "Total",
                            "Completion %",
                        ],
                        [
                            [
                                row.character,
                                format_expansion_label(row.section)
                                if row.section.casefold() == "everquest"
                                or any(row.section == name for name, _ in EXPANSIONS_NEWEST_FIRST)
                                else row.section,
                                row.completed,
                                row.incomplete,
                                row.total,
                                row.completion_pct,
                            ]
                            for row in ach.summaries
                        ],
                        character_column=0,
                        expansion_column=1,
                    ),
                }
            )

    gear_legend = build_gear_legend()

    prefix = default_export_prefix_from_report(report)

    return {
        "meta": {
            "version": __version__,
            "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "reportTitle": f"{prefix} Team Inventory" if prefix else "Team Inventory",
            "characterCount": len(report.characters),
            "characters": [
                {
                    "name": character.display_name,
                    "shortName": character.character,
                    "server": character.server,
                }
                for character in report.characters
            ],
            "logoDataUri": _eq_logo_data_uri(),
            "currentExpansion": format_expansion_label(EXPANSIONS_NEWEST_FIRST[0][0]),
        },
        "theme": {
            "gearSets": GEAR_SET_FILLS,
            "tierCodes": build_tier_code_colors(),
            "spellTiers": SPELL_TIER_COLORS,
        },
        "gearLegend": gear_legend,
        "expansionOrder": _expansion_filter_order(),
        "sections": sections,
    }


def write_team_html(bundle: ExportBundle, output_path: Path) -> Path:
    """Write a self-contained interactive HTML report."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template = read_data_text("team_report.html")
    if _REPORT_JSON_MARKER not in template:
        raise ValueError("HTML template is missing the report JSON marker.")

    payload = json.dumps(serialize_report(bundle), ensure_ascii=False)
    html = template.replace(_REPORT_JSON_MARKER, payload, 1)
    del payload, template, bundle
    output_path.write_text(html, encoding="utf-8")
    del html
    return output_path


def extract_report_json(html_text: str) -> dict:
    """Parse embedded report JSON from a generated HTML file (for tests)."""
    marker = "const REPORT = "
    start = html_text.index(marker) + len(marker)
    end = html_text.index(";\n", start)
    return json.loads(html_text[start:end])
