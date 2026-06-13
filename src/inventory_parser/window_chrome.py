"""OS-specific window chrome (dark title bar on Windows)."""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk

from inventory_parser.gui_theme import BG, FG

def _hex_to_colorref(hex_color: str) -> int:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return 0x00141212
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return red | (green << 8) | (blue << 16)


def apply_dark_title_bar(
    window: tk.Misc,
    *,
    background: str = BG,
    foreground: str = FG,
) -> None:
    """Match the mockup: dark native caption bar on Windows 10/11."""
    if sys.platform != "win32":
        return
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()

        dwm = ctypes.windll.dwmapi
        enabled = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (+ pre-20H1)
            dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(enabled), ctypes.sizeof(enabled))

        caption = ctypes.c_int(_hex_to_colorref(background))
        text = ctypes.c_int(_hex_to_colorref(foreground))
        for attr, value in ((35, caption), (36, text)):  # CAPTION_COLOR, TEXT_COLOR (Win11)
            dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
    except (AttributeError, OSError, ValueError):
        pass


def bind_dark_title_bar(window: tk.Misc, **colors: str) -> None:
    """Re-apply dark title bar when the window is shown or restored."""

    def _apply(_event: tk.Event | None = None) -> None:
        apply_dark_title_bar(window, **colors)

    window.after(0, _apply)
    window.bind("<Map>", _apply, add="+")
