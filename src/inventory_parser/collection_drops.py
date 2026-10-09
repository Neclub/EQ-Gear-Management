"""Where a collection drops, for the Missing Collections hover chip."""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache

from inventory_parser.package_data import read_data_text

_CATALOG_NAME = "collection_drops.json"

_ZERO_WIDTH = str.maketrans("", "", "\u200b\ufeff\u200c\u200d\u2060")
_APOSTROPHE_RE = re.compile(r"['\u2018\u2019\u02bc\u2032\u00b4`]")
_WS_RE = re.compile(r"\s+")
_TRAILING_PUNCT_RE = re.compile(r"[.!?]+$")


def normalize_collection_name(name: str) -> str:
    """Casefold, drop apostrophes and zero-width characters, strip trailing punctuation."""
    text = unicodedata.normalize("NFKC", name or "")
    text = text.translate(_ZERO_WIDTH)
    text = _APOSTROPHE_RE.sub("", text)
    text = _WS_RE.sub(" ", text).strip().casefold()
    return _TRAILING_PUNCT_RE.sub("", text).strip()


@lru_cache(maxsize=1)
def _catalog() -> dict[str, str]:
    raw = json.loads(read_data_text(_CATALOG_NAME))
    if not isinstance(raw, dict):
        return {}
    catalog: dict[str, str] = {}
    for key, value in raw.items():
        folded = normalize_collection_name(str(key))
        location = str(value or "").strip()
        if folded and location:
            catalog[folded] = location
    return catalog


def collection_drop_location(name: str) -> str | None:
    """Chip text for a collection, or None when the notes have no location."""
    folded = normalize_collection_name(name)
    if not folded:
        return None
    return _catalog().get(folded)
