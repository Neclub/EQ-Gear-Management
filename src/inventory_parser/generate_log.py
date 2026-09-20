"""Overwrite a single last-generate log under %LOCALAPPDATA%\\EQGM\\."""

from __future__ import annotations

import threading
from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from inventory_parser import APP_NAME_SHORT, __version__
from inventory_parser import character_column_order as _settings

LOG_FILENAME = "last_report.log"

# Stable display order for Cache lines.
CACHE_CATEGORY_ORDER: tuple[str, ...] = (
    "Prebuilt GitHub cache",
    "Character classes",
    "Gear T-levels",
    "Type 7/8 catalog",
    "Type 7/8 aug pages",
    "Item expansions",
    "Item sockets",
    "Type 18/19 catalog",
    "Type 18/19 item meta",
    "Raid BiS catalog",
    "Item details",
    "Item icons",
    "Expansion images",
)


def _website_group_for_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    path = (parsed.path or "").casefold()
    query = (parsed.query or "").casefold()
    if "raidloot.com" in host:
        return "raidloot"
    if "itemimages" in path or path.endswith(".png") or path.endswith(".jpg"):
        if "expac" in path or "expacimages" in path:
            return "Expansion images"
        return "Item icons"
    if "expacimages" in path:
        return "Expansion images"
    if "itemsearch" in path or "search" in path or "augtype" in query:
        return "Catalog searches"
    if "items.php" in path or "/items/" in path:
        return "Item pages"
    if "raidarmor" in path or "raidgear" in path or "raidvendor" in path:
        return "Raid BiS pages"
    return "Other"


_WEBSITE_GROUP_ORDER: tuple[str, ...] = (
    "Catalog searches",
    "Raid BiS pages",
    "Item pages",
    "Item icons",
    "Expansion images",
    "raidloot",
    "Other",
)


@dataclass
class FetchSnapshot:
    """Immutable copy of fetch activity for one generate run."""

    cache_counts: dict[str, int] = field(default_factory=dict)
    cache_details: dict[str, list[str]] = field(default_factory=dict)
    website_urls: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


class FetchRecorder:
    """Thread-safe collector for cache hits, website URLs, and fetch problems."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache_counts: dict[str, int] = defaultdict(int)
        self._cache_details: dict[str, list[str]] = defaultdict(list)
        self._website_urls: list[str] = []
        self._website_seen: set[str] = set()
        self._problems: list[str] = []
        self._problem_seen: set[str] = set()

    def record_cache(self, category: str, detail: str | None = None) -> None:
        cat = (category or "").strip()
        if not cat:
            return
        with self._lock:
            self._cache_counts[cat] += 1
            if detail:
                text = str(detail).strip()
                if text and text not in self._cache_details[cat]:
                    self._cache_details[cat].append(text)

    def record_website(self, url: str) -> None:
        text = (url or "").strip()
        if not text:
            return
        with self._lock:
            if text in self._website_seen:
                return
            self._website_seen.add(text)
            self._website_urls.append(text)

    def record_problem(self, message: str) -> None:
        text = (message or "").strip()
        if not text:
            return
        with self._lock:
            if text in self._problem_seen:
                return
            self._problem_seen.add(text)
            self._problems.append(text)

    def snapshot(self) -> FetchSnapshot:
        with self._lock:
            return FetchSnapshot(
                cache_counts=dict(self._cache_counts),
                cache_details={k: list(v) for k, v in self._cache_details.items()},
                website_urls=list(self._website_urls),
                problems=list(self._problems),
            )


_active_recorder: ContextVar[FetchRecorder | None] = ContextVar(
    "eqgm_fetch_recorder", default=None
)


@contextmanager
def fetch_recording() -> Iterator[FetchRecorder]:
    """Activate a FetchRecorder for the current context (generate worker thread)."""
    recorder = FetchRecorder()
    token = _active_recorder.set(recorder)
    try:
        yield recorder
    finally:
        _active_recorder.reset(token)


def current_fetch_recorder() -> FetchRecorder | None:
    return _active_recorder.get()


def record_cache(category: str, detail: str | None = None) -> None:
    recorder = current_fetch_recorder()
    if recorder is not None:
        recorder.record_cache(category, detail)


def record_website(url: str) -> None:
    recorder = current_fetch_recorder()
    if recorder is not None:
        recorder.record_website(url)


def record_problem(message: str) -> None:
    recorder = current_fetch_recorder()
    if recorder is not None:
        recorder.record_problem(message)


def last_report_log_path() -> Path:
    return _settings.settings_path().parent / LOG_FILENAME


def write_last_report_log(
    *,
    source: str,
    config: dict | None = None,
    result: dict | None = None,
    traceback_text: str | None = None,
    elapsed_seconds: float | None = None,
    fetch_snapshot: FetchSnapshot | None = None,
) -> Path | None:
    """Replace last_report.log with this run. Failures to write are ignored."""
    try:
        path = last_report_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        text = format_last_report_log(
            source=source,
            config=config or {},
            result=result,
            traceback_text=traceback_text,
            elapsed_seconds=elapsed_seconds,
            fetch_snapshot=fetch_snapshot,
        )
        tmp = path.with_name(f"{path.name}.tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        return path
    except OSError:
        return None


def format_last_report_log(
    *,
    source: str,
    config: dict,
    result: dict | None,
    traceback_text: str | None,
    elapsed_seconds: float | None,
    fetch_snapshot: FetchSnapshot | None = None,
) -> str:
    ok = bool(result and result.get("ok"))
    error = ""
    if result and not result.get("ok"):
        error = str(result.get("error") or "").strip()
    if traceback_text and not error:
        error = "Export failed."
    status = "ok" if ok and not traceback_text else "failed"
    elapsed = result.get("elapsedSeconds") if result else None
    if elapsed is None:
        elapsed = elapsed_seconds
    elapsed_s = f"{elapsed}s" if elapsed is not None else "—"
    characters = result.get("characterCount") if result else None
    if characters is None:
        order = config.get("characterColumnOrder") or []
        characters = len(order) if order else "—"

    warnings = (result or {}).get("warnings")
    lines = [
        f"{APP_NAME_SHORT} last generated report",
        "==========================",
        f"Time: {_now_stamp()}",
        f"Version: {__version__}",
        f"Source: {source or '—'}",
        f"Status: {status}",
        f"Elapsed: {elapsed_s}",
        f"Characters: {characters}",
        "",
        "Output",
        "------",
        f"Excel: {_result_path(result, 'xlsx')}",
        f"HTML: {_result_path(result, 'html')}",
        f"Format: {_output_format(config, result)}",
        "",
        "Options",
        "-------",
        f"Spells: {_yesno(config.get('includeSpells'))}",
        f"Achievements: {_yesno(config.get('includeAchievements'))}",
        f"Type 7/8 Augs: {_yesno(config.get('includeSlot2'))}",
        f"Type 5 Augs: {_yesno(config.get('includeType5'))}",
        f"Type 18/19 Augs: {_yesno(config.get('includeType18'))}",
        f"Raid BiS: {_yesno(config.get('includeRaidBis'))}",
        f"Anniversary augs: {_yesno(config.get('includeAnniversary'))}",
        f"Advanced weights: {_advanced_weights(config)}",
        "",
        "Input files",
        "-----------",
        *_path_block(config.get("paths")),
        "",
        "Roster order",
        "------------",
        *_path_block(config.get("characterColumnOrder")),
        "",
        "Warnings",
        "--------",
        *_path_block(warnings),
        "",
        *_format_fetches_section(fetch_snapshot),
        "",
        "Problems",
        "--------",
        *_format_problems_section(fetch_snapshot, warnings),
        "",
        "Error",
        "-----",
        error or "(none)",
    ]
    if traceback_text and traceback_text.strip():
        lines.extend(["", "Traceback", "---------", traceback_text.strip()])
    lines.append("")
    return "\n".join(lines)


def _format_fetches_section(snapshot: FetchSnapshot | None) -> list[str]:
    lines = ["Fetches", "-------", "Cache"]
    if snapshot is None or not snapshot.cache_counts:
        lines.append("  (none)")
    else:
        lines.extend(_format_cache_lines(snapshot))
    lines.append("Website")
    if snapshot is None or not snapshot.website_urls:
        lines.append("  (none)")
    else:
        lines.extend(_format_website_lines(snapshot.website_urls))
    return lines


def _format_cache_lines(snapshot: FetchSnapshot) -> list[str]:
    lines: list[str] = []
    ordered = list(CACHE_CATEGORY_ORDER) + sorted(
        c for c in snapshot.cache_counts if c not in CACHE_CATEGORY_ORDER
    )
    for cat in ordered:
        count = snapshot.cache_counts.get(cat)
        if not count:
            continue
        details = snapshot.cache_details.get(cat) or []
        if details and cat in ("Type 7/8 catalog", "Type 18/19 catalog", "Raid BiS catalog"):
            # Catalogs: show names, not a raw hit count of 1.
            joined = ", ".join(details)
            lines.append(f"  {cat}: {joined}" if joined else f"  {cat}")
        elif details and len(details) <= 12 and all(len(d) < 40 for d in details):
            lines.append(f"  {cat}: {count} ({', '.join(details)})")
        else:
            lines.append(f"  {cat}: {count}")
    return lines or ["  (none)"]


def _format_website_lines(urls: list[str]) -> list[str]:
    by_group: dict[str, list[str]] = defaultdict(list)
    for url in urls:
        by_group[_website_group_for_url(url)].append(url)
    lines: list[str] = []
    for group in _WEBSITE_GROUP_ORDER:
        group_urls = by_group.get(group) or []
        if not group_urls:
            continue
        lines.append(f"  {group} ({len(group_urls)})")
        for url in group_urls:
            lines.append(f"    {url}")
    for group, group_urls in sorted(by_group.items()):
        if group in _WEBSITE_GROUP_ORDER:
            continue
        lines.append(f"  {group} ({len(group_urls)})")
        for url in group_urls:
            lines.append(f"    {url}")
    return lines or ["  (none)"]


def _format_problems_section(
    snapshot: FetchSnapshot | None, warnings: object
) -> list[str]:
    warning_set = {
        str(item).strip()
        for item in (warnings or [])
        if str(item).strip()
    }
    problems: list[str] = []
    if snapshot is not None:
        for msg in snapshot.problems:
            text = msg.strip()
            if text and text not in warning_set:
                problems.append(text)
    return problems or ["(none)"]


def _now_stamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def _yesno(value: object) -> str:
    return "yes" if value else "no"


def _output_format(config: dict, result: dict | None) -> str:
    fmt = str(config.get("outputFormat") or "").strip()
    if fmt:
        return fmt
    if config.get("alsoHtml"):
        return "both"
    has_xlsx = bool(result and result.get("xlsx"))
    has_html = bool(result and result.get("html"))
    if has_xlsx and has_html:
        return "both"
    if has_html:
        return "html"
    if has_xlsx:
        return "excel"
    return "—"


def _advanced_weights(config: dict) -> str:
    if not config.get("advancedWeights"):
        return "no"
    weights = config.get("sessionWeights") or {}
    n = len(weights) if isinstance(weights, dict) else 0
    return f"yes ({n} stats)" if n else "yes"


def _result_path(result: dict | None, key: str) -> str:
    if not result:
        return "(none)"
    value = result.get(key)
    return str(value) if value else "(none)"


def _path_block(values: object) -> list[str]:
    if not values:
        return ["(none)"]
    if isinstance(values, str):
        text = values.strip()
        return [text] if text else ["(none)"]
    lines = [str(item).strip() for item in values if str(item).strip()]
    return lines or ["(none)"]
