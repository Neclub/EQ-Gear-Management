"""URL helpers and assets for the pywebview HTML GUI."""

from __future__ import annotations

import base64

from inventory_parser.package_data import asset_path, gui_asset_path


DEFAULT_WINDOW_WIDTH = 982
DEFAULT_WINDOW_HEIGHT = 765


def file_url(path) -> str:
    """Return a file:// URL for a local path."""
    return path.resolve().as_uri()


def setup_url() -> str:
    return file_url(gui_asset_path("setup.html"))


def eq_logo_data_uri() -> str:
    data = asset_path("eq-icon.png").read_bytes()
    encoded = base64.standard_b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"
