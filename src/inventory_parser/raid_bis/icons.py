"""Cache and embed EQ Resource item icons at generate time."""

from __future__ import annotations

import base64
import urllib.error
import urllib.request
from pathlib import Path

from inventory_parser.slot2_augs.eqresource_augs import USER_AGENT
from inventory_parser.slot2_augs.paths import appdata_dir

ICON_URL = "https://items.eqresource.com/itemimages/{icon_id}.png"


def icon_cache_dir() -> Path:
    path = appdata_dir() / "item_icons"
    path.mkdir(parents=True, exist_ok=True)
    return path


def collect_icon_data_uris(
    icon_ids: set[str],
    *,
    allow_network: bool = True,
) -> dict[str, str]:
    """Return icon_id → data URI. Missing icons are omitted (name links still work)."""
    out: dict[str, str] = {}
    for icon_id in sorted(icon_ids):
        if not icon_id or not str(icon_id).isdigit():
            continue
        png = _load_icon_png(str(icon_id), allow_network=allow_network)
        if not png:
            continue
        b64 = base64.b64encode(png).decode("ascii")
        out[str(icon_id)] = f"data:image/png;base64,{b64}"
    return out


def _load_icon_png(icon_id: str, *, allow_network: bool) -> bytes | None:
    path = icon_cache_dir() / f"{icon_id}.png"
    if path.is_file():
        try:
            data = path.read_bytes()
        except OSError:
            data = b""
        if data:
            return data
    if not allow_network:
        return None
    try:
        req = urllib.request.Request(
            ICON_URL.format(icon_id=icon_id),
            headers={"User-Agent": USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    if not data:
        return None
    try:
        path.write_bytes(data)
    except OSError:
        pass
    return data
