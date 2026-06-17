"""Python API exposed to the HTML GUI via pywebview."""

from __future__ import annotations

import json
import threading
import traceback
from pathlib import Path

import webview

from inventory_parser import __version__
from inventory_parser.achievement_files import collect_achievement_paths
from inventory_parser.character_column_order import (
    ColumnRosterEntry,
    build_column_roster,
    paths_for_roster_removal,
    save_character_column_order,
    saved_character_column_order,
)
from inventory_parser.eq_servers import server_display_name
from inventory_parser.excel_export import write_team_workbook
from inventory_parser.excel_theme import tier_bucket_legend_rows
from inventory_parser.export_bundle import build_export_bundle, release_export_memory
from inventory_parser.html_export import serialize_report
from inventory_parser.html_export import write_team_html
from inventory_parser.missing_spells import (
    bindings_include_personas,
    discover_persona_bindings,
    split_input_paths,
)
from inventory_parser.output_paths import (
    default_export_prefix_from_input_paths,
    html_path_for_workbook,
    is_auto_team_inventory_path,
    team_inventory_filename,
    team_inventory_path,
)
from inventory_parser.slots import NON_VISIBLE_SLOTS, VISIBLE_SLOTS, SlotFilter
from inventory_parser.team_report import FolderCharacterChoice, discover_folder_character_choices
from inventory_parser.web_bridge import eq_logo_data_uri, report_viewer_html, setup_url


def _downloads_dir() -> Path:
    return Path.home() / "Downloads"


def _roster_entry_dict(entry: ColumnRosterEntry) -> dict:
    return {
        "personaKey": entry.persona_key,
        "displayName": entry.display_name,
        "character": entry.character,
        "server": entry.server,
        "classAbbr": entry.class_abbr,
    }


def _choice_summary(choice: FolderCharacterChoice) -> str:
    parts: list[str] = []
    if choice.inventory_paths:
        n = len(choice.inventory_paths)
        parts.append(f"{n} inventory" if n != 1 else "1 inventory")
    if choice.spell_paths:
        n = len(choice.spell_paths)
        parts.append(f"{n} MissingSpells" if n != 1 else "1 MissingSpells")
    if choice.achievement_paths:
        n = len(choice.achievement_paths)
        parts.append(f"{n} Achievements" if n != 1 else "1 Achievements")
    return ", ".join(parts) if parts else "No files"


def _class_abbr_from_choice(choice: FolderCharacterChoice) -> str | None:
    from inventory_parser.missing_spells import parse_missing_spells_filename

    for path in choice.spell_paths:
        parsed = parse_missing_spells_filename(path)
        if parsed is not None:
            return parsed[2]
    return None


def _choice_dict(choice: FolderCharacterChoice) -> dict:
    class_abbr = _class_abbr_from_choice(choice)
    return {
        "character": choice.character,
        "server": choice.server,
        "serverDisplay": server_display_name(choice.server),
        "classAbbr": class_abbr,
        "inventoryCount": len(choice.inventory_paths),
        "spellCount": len(choice.spell_paths),
        "achievementCount": len(choice.achievement_paths),
        "summary": _choice_summary(choice),
        "paths": [str(p) for p in choice.paths],
    }


class WebApi:
    """JS-callable API for the HTML setup and report viewer."""

    def __init__(self) -> None:
        self._window: webview.Window | None = None

    def bind_window(self, window: webview.Window) -> None:
        self._window = window

    def get_version(self) -> dict:
        return {"version": __version__, "logoDataUri": eq_logo_data_uri()}

    def pick_folder(self) -> str | None:
        window = self._window
        if window is None:
            return None
        result = window.create_file_dialog(webview.FileDialog.FOLDER)
        if not result:
            return None
        return str(result[0])

    def pick_output_file(self, suggested_name: str) -> str | None:
        window = self._window
        if window is None:
            return None
        result = window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory=str(_downloads_dir()),
            save_filename=suggested_name,
            file_types=("Excel workbook (*.xlsx)", "All files (*.*)"),
        )
        if not result:
            return None
        path = Path(result)
        if path.suffix.lower() != ".xlsx":
            path = path.with_suffix(".xlsx")
        return str(path.resolve())

    def discover_folder_choices(self, folder: str) -> dict:
        folder_path = Path(folder)
        choices = discover_folder_character_choices(folder_path)
        servers = sorted({c.server for c in choices}, key=str.casefold)
        return {
            "folder": str(folder_path),
            "choices": [_choice_dict(c) for c in choices],
            "servers": [
                {"slug": slug, "label": server_display_name(slug)} for slug in servers
            ],
        }

    def split_paths(self, paths: list[str]) -> dict:
        inv, spells, achievements = split_input_paths([Path(p) for p in paths])
        return {
            "inventory": [str(p) for p in inv],
            "spells": [str(p) for p in spells],
            "achievements": [str(p) for p in achievements],
        }

    def build_roster(self, paths: list[str]) -> list[dict]:
        entries = build_column_roster(paths, saved_character_column_order())
        return [_roster_entry_dict(e) for e in entries]

    def save_roster_order(self, persona_keys: list[str]) -> None:
        save_character_column_order(persona_keys)

    def paths_for_removal(
        self,
        removing_keys: list[str],
        roster: list[dict],
        paths: list[str],
    ) -> list[str]:
        removing = [
            ColumnRosterEntry(
                persona_key=e["personaKey"],
                display_name=e["displayName"],
                character=e["character"],
                server=e["server"],
                class_abbr=e.get("classAbbr"),
            )
            for e in roster
            if e["personaKey"] in removing_keys
        ]
        full_roster = [
            ColumnRosterEntry(
                persona_key=e["personaKey"],
                display_name=e["displayName"],
                character=e["character"],
                server=e["server"],
                class_abbr=e.get("classAbbr"),
            )
            for e in roster
        ]
        drop = paths_for_roster_removal(removing, full_roster, paths)
        return sorted(drop)

    def spell_bindings(self, paths: list[str]) -> dict:
        inv, spells, _ = split_input_paths([Path(p) for p in paths])
        discovery = discover_persona_bindings(inv, spell_paths=spells or None)
        spell_count = sum(1 for b in discovery.bindings if b.spell_path)
        return {
            "hasSpells": bool(spell_count),
            "spellCount": spell_count,
            "usePersonaLabel": bindings_include_personas(discovery.bindings),
            "warnings": list(discovery.warnings),
        }

    def achievement_info(self, paths: list[str]) -> dict:
        inv, _, achievements = split_input_paths([Path(p) for p in paths])
        discovered = collect_achievement_paths(inv, achievements or None)
        count = len(achievements) if achievements else len(discovered)
        return {"hasAchievements": bool(count), "achievementCount": count}

    def default_output_path(self, paths: list[str], current: str) -> str:
        prefix = default_export_prefix_from_input_paths([Path(p) for p in paths])
        if not current.strip() or is_auto_team_inventory_path(current):
            return str(team_inventory_path(_downloads_dir(), prefix))
        return current

    def default_output_filename(self, paths: list[str]) -> str:
        prefix = default_export_prefix_from_input_paths([Path(p) for p in paths])
        return team_inventory_filename(prefix)

    def tier_legend(self) -> dict:
        rows = []
        for fill, label in tier_bucket_legend_rows():
            rows.append({"color": fill.fgColor.rgb[-6:], "label": label})
        return {
            "rows": rows,
            "visibleSlots": list(VISIBLE_SLOTS),
            "nonVisibleSlots": list(NON_VISIBLE_SLOTS),
        }

    def navigate_to_setup(self) -> None:
        window = self._window
        if window is not None:
            window.load_url(setup_url())

    def generate_report(self, config: dict) -> dict:
        """Start report generation on a background thread."""
        window = self._window
        if window is None:
            return {"ok": False, "error": "Window not ready."}

        def work() -> None:
            try:
                result = self._generate_report_sync(config)
                payload = json.dumps(result, ensure_ascii=False)
                window.evaluate_js(f"window.onGenerateComplete({payload})")
            except Exception as exc:
                tb = traceback.format_exc()
                err = json.dumps({"ok": False, "error": str(exc), "traceback": tb})
                window.evaluate_js(f"window.onGenerateComplete({err})")
            finally:
                release_export_memory()

        threading.Thread(target=work, daemon=True).start()
        return {"ok": True, "started": True}

    def _generate_report_sync(self, config: dict) -> dict:
        paths = [Path(p) for p in config.get("paths", [])]
        output = config.get("outputPath", "").strip()
        inv_paths, _, _ = split_input_paths(paths)
        if not inv_paths:
            return {
                "ok": False,
                "error": "Add at least one *-Inventory.txt file (MissingSpells alone is not enough).",
            }
        if not output:
            return {"ok": False, "error": "Choose where to save the Excel file."}

        raw_slots = (config.get("slotFilter") or "all").strip()
        slot_filter: SlotFilter = (
            raw_slots if raw_slots in ("all", "visible", "non_visible") else "all"
        )
        include_spells = bool(config.get("includeSpells"))
        include_achievements = bool(config.get("includeAchievements"))
        also_html = bool(config.get("alsoHtml", True))
        column_order = config.get("characterColumnOrder") or None

        try:
            bundle = build_export_bundle(
                paths,
                slot_filter=slot_filter,
                include_spells=include_spells,
                include_achievements=include_achievements,
                character_column_order=column_order,
            )
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

        warnings = list(bundle.warnings)
        report_payload = serialize_report(bundle)

        output_path = Path(output)
        saved = write_team_workbook(
            bundle.team,
            output_path,
            slot_filter=bundle.slot_filter,
            spell_report=bundle.spell_report,
            rune_inventory_report=bundle.rune_inventory_report,
            achievement_report=bundle.achievement_report,
        )
        html_saved = None
        if also_html:
            html_saved = write_team_html(bundle, html_path_for_workbook(saved))

        char_count = len(bundle.team.characters)
        return {
            "ok": True,
            "xlsx": str(saved),
            "html": str(html_saved) if html_saved is not None else None,
            "warnings": warnings,
            "reportPayload": report_payload if char_count > 1 else None,
        }

    def show_report(self, report_payload: dict) -> None:
        """Load the in-app report viewer with the given payload."""
        window = self._window
        if window is None:
            return
        payload_json = json.dumps(report_payload, ensure_ascii=False)
        html = report_viewer_html(payload_json)
        window.load_html(html)
