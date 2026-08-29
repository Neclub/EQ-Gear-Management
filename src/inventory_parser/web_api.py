"""Python API exposed to the HTML GUI via pywebview."""

from __future__ import annotations

import json
import re
import threading
import time
import webbrowser
from pathlib import Path

import webview

from inventory_parser import __version__
from inventory_parser.achievement_files import collect_achievement_paths
from inventory_parser.app_updates import check_for_updates as fetch_app_updates
from inventory_parser.app_updates import is_allowed_download_url
from inventory_parser.character_column_order import (
    ColumnRosterEntry,
    build_column_roster,
    normalize_output_format,
    paths_for_roster_removal,
    reset_tier_colors,
    save_character_column_order,
    save_eq_folder,
    save_output_format,
    save_tier_color,
    saved_character_column_order,
    saved_eq_folder,
    saved_output_format,
    tier_colors_are_custom,
)
from inventory_parser.eq_servers import server_display_name
from inventory_parser.excel_export import write_team_workbook
from inventory_parser.excel_theme import tier_legend_entries
from inventory_parser.export_bundle import build_export_bundle, release_export_memory
from inventory_parser.slot2_augs.build import report_progress
from inventory_parser.slot2_augs.weights import default_class_weights, sanitize_weight_map
from inventory_parser.html_export import write_team_html
from inventory_parser.missing_spells import (
    bindings_include_personas,
    discover_persona_bindings,
    split_input_paths,
)
from inventory_parser.output_paths import (
    apply_default_export_filename,
    default_export_prefix_from_input_paths,
    html_path_for_workbook,
    output_directory_from_current,
    team_inventory_filename,
    team_inventory_path,
)
from inventory_parser.slots import NON_VISIBLE_SLOTS, VISIBLE_SLOTS, SlotFilter
from inventory_parser.team_report import FolderCharacterChoice, discover_folder_character_choices
from inventory_parser.web_bridge import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    eq_logo_data_uri,
    file_url,
    setup_url,
)

PRODUCT_WEBSITE_URL = "https://neclub.github.io/EQ-Gear-Management/"

_HOME_PATH = str(Path.home())
_HOME_PATH_RE = re.compile(re.escape(_HOME_PATH), re.IGNORECASE) if _HOME_PATH else None


def _downloads_dir() -> Path:
    return Path.home() / "Downloads"


def _first_dialog_selection(result: object) -> str | None:
    """pywebview dialogs return a tuple/list of paths, or None if cancelled."""
    if result is None or result is False:
        return None
    if isinstance(result, (list, tuple)):
        if not result:
            return None
        first = result[0]
    else:
        first = result
    if first is None or first is False:
        return None
    text = str(first).strip()
    return text or None


def _public_error_message(exc: BaseException) -> str:
    """User-facing error text without home-directory paths or tracebacks."""
    text = str(exc).strip() or type(exc).__name__
    if _HOME_PATH_RE is not None and _HOME_PATH:
        text = _HOME_PATH_RE.sub("~", text)
    return text


def _gui_error_payload(exc: BaseException) -> dict:
    return {"ok": False, "error": _public_error_message(exc)}


def _native_hwnd(window) -> int | None:
    native = getattr(window, "native", None)
    if native is None:
        return None
    handle = getattr(native, "Handle", None)
    if handle is None:
        return None
    try:
        return int(handle)
    except (TypeError, ValueError):
        return None


def _work_area_for_hwnd(hwnd: int | None) -> tuple[int, int, int, int]:
    """Monitor work area (left, top, right, bottom), excluding the taskbar."""
    try:
        import ctypes
        from ctypes import wintypes

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG),
            ]

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFlags", wintypes.DWORD),
            ]

        user32 = ctypes.windll.user32
        MONITOR_DEFAULTTONEAREST = 2
        if hwnd:
            monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        else:
            point = wintypes.POINT(0, 0)
            monitor = user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            raise OSError("GetMonitorInfoW failed")
        work = info.rcWork
        return int(work.left), int(work.top), int(work.right), int(work.bottom)
    except Exception:
        screens = getattr(webview, "screens", None) or []
        if screens:
            screen = screens[0]
            return 0, 0, int(screen.width), max(640, int(screen.height) - 48)
        return 0, 0, 1920, 1040


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

    def fit_window(self, min_width: int = 0, min_height: int = 0) -> dict:
        """Grow the GUI window so content stays visible within the work area."""
        window = self._window
        if window is None:
            return {"ok": False}
        if getattr(window, "maximized", False) or getattr(window, "fullscreen", False):
            return {"ok": True, "skipped": True}
        hwnd = _native_hwnd(window)
        left, top, right, bottom = _work_area_for_hwnd(hwnd)
        max_w = max(DEFAULT_WINDOW_WIDTH, right - left)
        max_h = max(640, bottom - top)
        width = min(max(DEFAULT_WINDOW_WIDTH, int(min_width or 0)), max_w)
        height = min(max(640, int(min_height or 0)), max_h)
        window.resize(width, height)
        x = int(getattr(window, "x", 0) or 0)
        y = int(getattr(window, "y", 0) or 0)
        if x + width > right:
            x = right - width
        if y + height > bottom:
            y = bottom - height
        if x < left:
            x = left
        if y < top:
            y = top
        try:
            window.move(x, y)
        except Exception:
            pass
        return {"ok": True, "width": width, "height": height, "x": x, "y": y}

    def start_window_drag(self) -> dict:
        """Begin a native title-bar drag from the custom header or modal."""
        window = self._window
        if window is None:
            return {"ok": False}
        if getattr(window, "maximized", False) or getattr(window, "fullscreen", False):
            return {"ok": True, "skipped": True}
        hwnd = _native_hwnd(window)
        if not hwnd:
            return {"ok": False}
        try:
            import ctypes

            user32 = ctypes.windll.user32
            WM_NCLBUTTONDOWN = 0x00A1
            HTCAPTION = 2
            user32.ReleaseCapture()
            user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)
            return {"ok": True}
        except Exception:
            return {"ok": False}

    def get_version(self) -> dict:
        return {
            "version": __version__,
            "logoDataUri": eq_logo_data_uri(),
            "websiteUrl": PRODUCT_WEBSITE_URL,
        }

    def check_for_updates(self) -> dict:
        return fetch_app_updates()

    def open_website(self) -> dict:
        webbrowser.open(PRODUCT_WEBSITE_URL)
        return {"ok": True, "url": PRODUCT_WEBSITE_URL}

    def open_update_download(self, url: str) -> dict:
        if not is_allowed_download_url(url):
            return {"ok": False, "error": "Unexpected download URL."}
        webbrowser.open(url)
        return {"ok": True}

    def get_gui_prefs(self) -> dict:
        return {
            "outputFormat": saved_output_format(),
            "lastEqFolder": saved_eq_folder(),
        }

    def set_output_format(self, value: str) -> dict:
        return {"outputFormat": save_output_format(value)}

    def get_class_weight_defaults(
        self, class_abbr: str | None = None, profile: str | None = None
    ) -> dict:
        """Return Head-slot default weights for Advanced Slot2 options."""
        return default_class_weights(class_abbr, profile=profile)

    def pick_folder(self) -> str | None:
        window = self._window
        if window is None:
            return None
        kwargs: dict = {}
        start = saved_eq_folder()
        if start:
            kwargs["directory"] = start
        result = window.create_file_dialog(webview.FileDialog.FOLDER, **kwargs)
        selected = _first_dialog_selection(result)
        if not selected:
            return None
        folder = str(Path(selected).resolve())
        save_eq_folder(folder)
        return folder

    def pick_output_folder(self, current: str = "") -> str | None:
        """Choose a destination folder; the export filename is applied separately."""
        window = self._window
        if window is None:
            return None
        kwargs: dict = {}
        start = output_directory_from_current(current, default=_downloads_dir())
        if start.is_dir():
            kwargs["directory"] = str(start)
        result = window.create_file_dialog(webview.FileDialog.FOLDER, **kwargs)
        selected = _first_dialog_selection(result)
        if not selected:
            return None
        return str(Path(selected).resolve())

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
        return str(
            apply_default_export_filename(current, prefix, default_dir=_downloads_dir())
        )

    def default_output_filename(self, paths: list[str]) -> str:
        prefix = default_export_prefix_from_input_paths([Path(p) for p in paths])
        return team_inventory_filename(prefix)

    def tier_legend(self) -> dict:
        rows = tier_legend_entries()
        return {
            "rows": rows,
            "isCustom": tier_colors_are_custom(),
            "visibleSlots": list(VISIBLE_SLOTS),
            "nonVisibleSlots": list(NON_VISIBLE_SLOTS),
        }

    def set_tier_color(self, key: str, value: str) -> dict:
        colors = save_tier_color(key, value)
        return {
            "colors": colors,
            "isCustom": tier_colors_are_custom(colors),
            "rows": tier_legend_entries(),
        }

    def reset_tier_colors(self) -> dict:
        colors = reset_tier_colors()
        return {
            "colors": colors,
            "isCustom": False,
            "rows": tier_legend_entries(),
        }

    def navigate_to_setup(self) -> None:
        window = self._window
        if window is not None:
            window.load_url(setup_url())

    def _notify_progress(self, payload: dict) -> None:
        window = self._window
        if window is None:
            return
        try:
            window.evaluate_js(
                f"window.onGenerateProgress && window.onGenerateProgress({json.dumps(payload)})"
            )
        except Exception:
            pass

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
                err = json.dumps(_gui_error_payload(exc), ensure_ascii=False)
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
            return {"ok": False, "error": "Choose where to save the report."}
        prefix = default_export_prefix_from_input_paths(paths)
        output_choice = Path(output)
        if output_choice.is_dir() or not output_choice.suffix:
            output = str(team_inventory_path(output_choice, prefix))

        raw_slots = (config.get("slotFilter") or "all").strip()
        slot_filter: SlotFilter = (
            raw_slots if raw_slots in ("all", "visible", "non_visible") else "all"
        )
        include_spells = bool(config.get("includeSpells"))
        include_achievements = bool(config.get("includeAchievements"))
        include_slot2 = bool(config.get("includeSlot2"))
        include_type5 = bool(config.get("includeType5"))
        include_type18 = bool(config.get("includeType18"))
        include_raid_bis = bool(config.get("includeRaidBis"))
        include_anniversary = bool(config.get("includeAnniversary"))
        session_weights = None
        if include_slot2 and config.get("advancedWeights") and config.get("sessionWeights"):
            session_weights = sanitize_weight_map(config.get("sessionWeights") or {})
        if "outputFormat" in config:
            output_format = normalize_output_format(config.get("outputFormat"))
        elif "alsoHtml" in config:
            output_format = "both" if config.get("alsoHtml") else "excel"
        else:
            output_format = normalize_output_format(None)
        write_excel = output_format in ("excel", "both")
        write_html = output_format in ("html", "both")
        column_order = config.get("characterColumnOrder") or None
        started = time.perf_counter()

        def on_progress(payload: dict) -> None:
            self._notify_progress(payload)

        try:
            bundle = build_export_bundle(
                paths,
                slot_filter=slot_filter,
                include_spells=include_spells,
                include_achievements=include_achievements,
                include_slot2=include_slot2,
                include_type5=include_type5,
                include_type18=include_type18,
                include_raid_bis=include_raid_bis,
                include_anniversary=include_anniversary,
                session_weights=session_weights,
                on_progress=on_progress,
                character_column_order=column_order,
            )
        except ValueError as exc:
            return _gui_error_payload(exc)

        warnings = list(bundle.warnings)

        output_path = Path(output)
        saved = None
        html_saved = None
        if include_slot2 or include_type5 or include_type18 or include_raid_bis:
            report_progress(on_progress, "Writing Excel/HTML…", 0.95, 1.0, 0, 1)
        if write_excel:
            saved = write_team_workbook(
                bundle.team,
                output_path,
                slot_filter=bundle.slot_filter,
                spell_report=bundle.spell_report,
                missing_useful_report=bundle.missing_useful_report,
                rune_inventory_report=bundle.rune_inventory_report,
                achievement_report=bundle.achievement_report,
                unmade_entries=bundle.unmade_entries,
                slot2=bundle.slot2,
                type5=bundle.type5,
                type18=bundle.type18,
                raid_bis=bundle.raid_bis,
            )
            if write_html:
                html_saved = write_team_html(bundle, html_path_for_workbook(saved))
        elif write_html:
            if output_path.suffix.lower() == ".xlsx":
                html_target = html_path_for_workbook(output_path)
            elif output_path.suffix.lower() == ".html":
                html_target = output_path
            else:
                html_target = html_path_for_workbook(output_path.with_suffix(".xlsx"))
            html_saved = write_team_html(bundle, html_target)
        if include_slot2 or include_type5 or include_type18 or include_raid_bis:
            report_progress(on_progress, "Done", 0.95, 1.0, 1, 1)

        elapsed = round(time.perf_counter() - started, 1)
        return {
            "ok": True,
            "xlsx": str(saved) if saved is not None else None,
            "html": str(html_saved) if html_saved is not None else None,
            "warnings": warnings,
            "elapsedSeconds": elapsed,
            "characterCount": len(bundle.team.characters),
        }

    def open_html_report(self, html_path: str) -> dict:
        """Open a saved HTML report in the system default browser."""
        path = Path(html_path)
        if not path.is_file():
            return {"ok": False, "error": f"HTML file not found: {html_path}"}
        webbrowser.open(file_url(path))
        return {"ok": True, "path": str(path)}
