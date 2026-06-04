"""Load bundled JSON data in development and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def data_dir() -> Path:
    """Directory containing package JSON files."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "inventory_parser" / "data"
    return Path(__file__).resolve().parent / "data"


def read_data_text(filename: str) -> str:
    path = data_dir() / filename
    if not path.is_file():
        raise FileNotFoundError(f"Package data file not found: {filename} ({path})")
    return path.read_text(encoding="utf-8")
