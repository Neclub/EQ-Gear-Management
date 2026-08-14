"""Pywebview HTML GUI entry point."""

from __future__ import annotations

import webview

from inventory_parser import APP_NAME, APP_NAME_SHORT, __version__
from inventory_parser.package_data import asset_path
from inventory_parser.web_api import WebApi
from inventory_parser.web_bridge import setup_url


def main() -> None:
    api = WebApi()
    window = webview.create_window(
        f"{APP_NAME} v{__version__}",
        url=setup_url(),
        js_api=api,
        width=860,
        height=640,
        min_size=(640, 480),
        background_color="#0b0e11",
    )
    api.bind_window(window)
    webview.start(debug=False, icon=str(asset_path("eq-icon.ico")))


if __name__ == "__main__":
    main()
