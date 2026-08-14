"""AppData root for EQGM caches (same folder as settings)."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.character_column_order import settings_path


def appdata_dir() -> Path:
    root = settings_path().parent
    root.mkdir(parents=True, exist_ok=True)
    return root
