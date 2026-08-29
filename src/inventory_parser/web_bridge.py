"""URL helpers and assets for the pywebview HTML GUI."""

from __future__ import annotations

import base64

from inventory_parser.package_data import asset_path, gui_asset_path, read_data_text
from inventory_parser.html_export import _REPORT_JSON_MARKER, escape_json_for_script


DEFAULT_WINDOW_WIDTH = 982
DEFAULT_WINDOW_HEIGHT = 765


def file_url(path) -> str:
    """Return a file:// URL for a local path."""
    return path.resolve().as_uri()


def setup_url() -> str:
    return file_url(gui_asset_path("setup.html"))


def report_viewer_html(payload_json: str | None = None) -> str:
    """Return report HTML for in-app viewing (marker replaced with null or payload)."""
    template = read_data_text("team_report.html")
    if _REPORT_JSON_MARKER not in template:
        raise ValueError("HTML template is missing the report JSON marker.")
    if payload_json is None:
        replacement = "null"
    else:
        replacement = escape_json_for_script(payload_json)
    return template.replace(_REPORT_JSON_MARKER, replacement, 1)


def eq_logo_data_uri() -> str:
    data = asset_path("eq-icon.png").read_bytes()
    encoded = base64.standard_b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"
