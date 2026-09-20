"""Cache and embed EQ Resource item icons at generate time."""

from __future__ import annotations

import base64
import urllib.error
from collections.abc import Callable
from pathlib import Path

from inventory_parser.generate_log import record_cache, record_problem
from inventory_parser.http_fetch import MAX_ICON_BYTES, http_get_bytes, is_png
from inventory_parser.slot2_augs.eqresource_augs import USER_AGENT
from inventory_parser.slot2_augs.paths import appdata_dir

ICON_URL = "https://items.eqresource.com/itemimages/{icon_id}.png"
# Shard so each folder stays under GitHub's ~1000-file directory listing limit.
ICON_SHARD_SIZE = 1000

StatusFn = Callable[[str, int, int], None]


def icon_cache_dir() -> Path:
    path = appdata_dir() / "item_icons"
    path.mkdir(parents=True, exist_ok=True)
    return path


def icon_shard_name(icon_id: str | int) -> str:
    """Return shard folder name for an icon id (``id // 1000``)."""
    return str(int(icon_id) // ICON_SHARD_SIZE)


def icon_png_path(icon_id: str | int, *, cache_dir: Path | None = None) -> Path:
    """Canonical on-disk path for newly written icons: flat ``{id}.png``."""
    root = cache_dir if cache_dir is not None else icon_cache_dir()
    return root / f"{icon_id}.png"


def resolve_icon_png_path(icon_id: str | int, *, cache_dir: Path | None = None) -> Path | None:
    """Return an existing icon path (sharded preferred, flat legacy fallback)."""
    root = cache_dir if cache_dir is not None else icon_cache_dir()
    text = str(icon_id)
    if not text.isdigit():
        return None
    sharded = root / icon_shard_name(text) / f"{text}.png"
    if sharded.is_file():
        return sharded
    legacy = root / f"{text}.png"
    if legacy.is_file():
        return legacy
    return None


def collect_icon_data_uris(
    icon_ids: set[str],
    *,
    allow_network: bool = True,
    on_status: StatusFn | None = None,
) -> dict[str, str]:
    """Return icon_id → data URI. Missing icons are omitted (name links still work)."""
    ids = [str(icon_id) for icon_id in sorted(icon_ids) if icon_id and str(icon_id).isdigit()]
    missing = [
        icon_id
        for icon_id in ids
        if resolve_icon_png_path(icon_id) is None
    ]
    if missing and allow_network and on_status is not None:
        on_status("Fetching item icons from EQ Resource…", 0, len(missing))
    elif ids and on_status is not None:
        on_status("Using cached item icons…", 1, 1)

    out: dict[str, str] = {}
    fetched = 0
    for icon_id in ids:
        png = _load_icon_png(icon_id, allow_network=allow_network)
        if not png:
            if icon_id in missing and allow_network:
                fetched += 1
                if on_status is not None:
                    on_status(
                        f"Fetching item icons from EQ Resource… ({fetched}/{len(missing)})",
                        fetched,
                        len(missing),
                    )
            continue
        b64 = base64.b64encode(png).decode("ascii")
        out[icon_id] = f"data:image/png;base64,{b64}"
        if icon_id in missing and allow_network:
            fetched += 1
            if on_status is not None:
                on_status(
                    f"Fetching item icons from EQ Resource… ({fetched}/{len(missing)})",
                    fetched,
                    len(missing),
                )
    return out


def _load_icon_png(icon_id: str, *, allow_network: bool) -> bytes | None:
    if not icon_id.isdigit():
        return None
    existing = resolve_icon_png_path(icon_id)
    if existing is not None:
        try:
            data = existing.read_bytes()
        except OSError:
            data = b""
        if is_png(data):
            record_cache("Item icons")
            return data
    if not allow_network:
        return None
    url = ICON_URL.format(icon_id=icon_id)
    try:
        data = http_get_bytes(
            url,
            timeout=20,
            user_agent=USER_AGENT,
            max_bytes=MAX_ICON_BYTES,
        )
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None
    if not is_png(data):
        record_problem(f"Item icon {url}: response was not a PNG")
        return None
    path = icon_png_path(icon_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    except OSError:
        # Cache write failed; still return the fetched icon bytes for this run.
        pass
    return data
