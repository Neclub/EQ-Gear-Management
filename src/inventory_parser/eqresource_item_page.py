"""Disk cache of EQ Resource item pages (items.php?id=).

One HTML file per item id. A later lookup of the same id, including odd
Range gear and old augments that are not in a catalog, reads the file
instead of downloading again.
"""

from __future__ import annotations

import threading
import urllib.error

from inventory_parser.generate_log import record_cache
from inventory_parser.http_fetch import http_get_text
from inventory_parser.items import EQRESOURCE_ITEM_URL
from inventory_parser.slot2_augs.paths import ITEM_PAGE_DIRNAME, appdata_dir

_id_locks_guard = threading.Lock()
_id_locks: dict[int, threading.Lock] = {}


def item_page_path(item_id: int):
    return appdata_dir() / ITEM_PAGE_DIRNAME / f"{int(item_id)}.html"


def cached_item_page_html(item_id: int) -> str | None:
    """Return a saved page without logging or touching the network."""
    if item_id <= 0:
        return None
    path = item_page_path(item_id)
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return text or None


def _lock_for(item_id: int) -> threading.Lock:
    with _id_locks_guard:
        lock = _id_locks.get(item_id)
        if lock is None:
            lock = threading.Lock()
            _id_locks[item_id] = lock
        return lock


def _is_item_page(html: str) -> bool:
    from inventory_parser.slot2_augs.eqresource_augs import _NAME_RE

    return bool(html and _NAME_RE.search(html))


def _write_page(item_id: int, html: str) -> None:
    path = item_page_path(item_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def get_eqresource_item_html(
    item_id: int,
    *,
    allow_network: bool = True,
    force_refresh: bool = False,
    timeout: float = 45.0,
) -> str | None:
    """Load an item page from disk, or download and save it once.

    Network errors and bodies without the EQ Resource item-name markup are
    not written, so the next Generate Report can retry. ``force_refresh``
    downloads again and replaces the file when the new body is a real item page.
    """
    if item_id <= 0:
        return None
    if not force_refresh:
        cached = cached_item_page_html(item_id)
        if cached is not None:
            record_cache("Item pages")
            return cached
    if not allow_network:
        return cached_item_page_html(item_id) if force_refresh else None

    with _lock_for(item_id):
        if not force_refresh:
            cached = cached_item_page_html(item_id)
            if cached is not None:
                record_cache("Item pages")
                return cached
        from inventory_parser.slot2_augs.eqresource_augs import USER_AGENT

        try:
            html = http_get_text(
                EQRESOURCE_ITEM_URL.format(item_id=item_id),
                timeout=timeout,
                user_agent=USER_AGENT,
            )
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise
        if _is_item_page(html):
            _write_page(item_id, html)
        return html
