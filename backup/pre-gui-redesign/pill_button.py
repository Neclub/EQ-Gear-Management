"""Pill-shaped tkinter button with variant colors matching the GUI theme."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageDraw, ImageTk

_FG = "#e8eaef"
_FG_MUTED = "#9ca3b4"
_ACCENT_EXCEL = "#3d9b5c"
_ACCENT_EXCEL_ACTIVE = "#2f7a47"
_ACCENT_DANGER = "#c45c5c"
_ACCENT_DANGER_ACTIVE = "#a04848"
_FALLBACK_BG = "#121214"
_AA_SCALE = 3

_VARIANT_PADDING: dict[str, tuple[tuple[int, int], tuple[str, int, str] | tuple[str, int]]] = {
    "default": ((10, 6), ("Segoe UI", 10)),
    "primary": ((10, 6), ("Segoe UI", 10)),
    "secondary": ((10, 6), ("Segoe UI", 10)),
    "danger": ((10, 6), ("Segoe UI", 10)),
    "accent": ((18, 11), ("Segoe UI", 11, "bold")),
}


@dataclass(frozen=True)
class _PillColors:
    fill: str
    fill_hover: str
    fill_disabled: str
    fg: str
    fg_disabled: str


_VARIANTS: dict[str, _PillColors] = {
    "default": _PillColors("#35353d", "#454550", "#2a2a32", _FG, _FG_MUTED),
    "primary": _PillColors("#3d6fad", "#4a7ec4", "#2a2a32", "#ffffff", _FG_MUTED),
    "secondary": _PillColors("#3d857a", "#4a9e92", "#2a2a32", "#ffffff", _FG_MUTED),
    "danger": _PillColors(_ACCENT_DANGER, _ACCENT_DANGER_ACTIVE, "#2a2a32", "#ffffff", _FG_MUTED),
    "accent": _PillColors(_ACCENT_EXCEL, _ACCENT_EXCEL_ACTIVE, "#2a2a32", "#ffffff", _FG_MUTED),
}


def _parent_bg(parent: tk.Misc) -> str:
    try:
        return str(parent.cget("background"))
    except tk.TclError:
        pass
    try:
        style = ttk.Style(parent)
        try:
            style_name = str(parent.cget("style"))
            bg = style.lookup(style_name, "background")
            if bg:
                return str(bg)
        except tk.TclError:
            pass
        widget_class = parent.winfo_class()
        bg = style.lookup(widget_class, "background")
        if bg:
            return str(bg)
        return str(style.lookup("TFrame", "background"))
    except tk.TclError:
        return _FALLBACK_BG


def _hex_to_rgba(color: str) -> tuple[int, int, int, int]:
    value = color.lstrip("#")
    if len(value) != 6:
        return 0, 0, 0, 255
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), 255


def _render_pill_rgba(width: int, height: int, fill: str) -> Image.Image:
    """Render an anti-aliased pill at higher resolution, then downscale."""
    scale = _AA_SCALE
    src_w = max(width * scale, 1)
    src_h = max(height * scale, 1)
    radius = src_h // 2
    image = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, src_w - 1, src_h - 1), radius=radius, fill=_hex_to_rgba(fill))
    if scale > 1:
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    return image


class PillButton(tk.Frame):
    """Capsule-shaped button drawn on a canvas."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str = "",
        command: Callable[[], None] | None = None,
        variant: str = "default",
        **kwargs: object,
    ) -> None:
        bg = _parent_bg(parent)
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0)
        self._text = text
        self._command = command
        self._variant = variant if variant in _VARIANTS else "default"
        self._state = tk.NORMAL
        self._hover = False
        self._pill_image: ImageTk.PhotoImage | None = None
        self._image_name = f"inventory_parser_pill_{id(self)}"

        padx, pady = _VARIANT_PADDING[self._variant][0]
        font_spec = _VARIANT_PADDING[self._variant][1]
        self._font = tkfont.Font(font=font_spec)
        self._padx = padx
        self._pady = pady

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self._canvas.pack()

        for widget in (self, self._canvas):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

        self._redraw()

    def _colors(self) -> _PillColors:
        return _VARIANTS[self._variant]

    def _fill_color(self) -> str:
        colors = self._colors()
        if self._state == tk.DISABLED:
            return colors.fill_disabled
        if self._hover:
            return colors.fill_hover
        return colors.fill

    def _text_color(self) -> str:
        colors = self._colors()
        if self._state == tk.DISABLED:
            return colors.fg_disabled
        return colors.fg

    def _release_pill_image(self) -> None:
        self._pill_image = None
        try:
            self.tk.call("image", "delete", self._image_name)
        except tk.TclError:
            pass

    def _on_enter(self, _event: tk.Event) -> None:
        if self._state == tk.DISABLED:
            return
        self._hover = True
        self._canvas.configure(cursor="hand2")
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        if self._state == tk.DISABLED:
            self._canvas.configure(cursor="")
        else:
            self._canvas.configure(cursor="hand2")
        self._redraw()

    def _on_click(self, _event: tk.Event) -> None:
        if self._state == tk.DISABLED or self._command is None:
            return
        self._command()

    def _redraw(self) -> None:
        self._release_pill_image()
        self._canvas.delete("all")
        text_w = self._font.measure(self._text)
        width = max(text_w + self._padx * 2, self._pady * 4)
        height = self._font.metrics("linespace") + self._pady * 2

        self._canvas.configure(width=width, height=height)
        self.configure(width=width, height=height)

        fill = self._fill_color()
        rgba = _render_pill_rgba(width, height, fill)
        try:
            self._pill_image = ImageTk.PhotoImage(rgba, name=self._image_name, master=self)
        finally:
            rgba.close()
        self._canvas.create_image(width // 2, height // 2, image=self._pill_image)
        self._canvas.create_text(
            width // 2,
            height // 2,
            text=self._text,
            fill=self._text_color(),
            font=self._font,
        )

        if self._state == tk.DISABLED:
            self._canvas.configure(cursor="")
        else:
            self._canvas.configure(cursor="hand2")

    def configure(self, cnf: dict[str, object] | None = None, **kw: object) -> dict[str, object] | None:
        if cnf:
            kw = {**cnf, **kw}
        redraw = False
        if "state" in kw:
            self._state = str(kw.pop("state"))
            redraw = True
        if "text" in kw:
            self._text = str(kw.pop("text"))
            redraw = True
        if "command" in kw:
            self._command = kw.pop("command")  # type: ignore[assignment]
            redraw = True
        if "variant" in kw:
            variant = str(kw.pop("variant"))
            if variant in _VARIANTS:
                self._variant = variant
                padx, pady = _VARIANT_PADDING[self._variant][0]
                font_spec = _VARIANT_PADDING[self._variant][1]
                self._font = tkfont.Font(font=font_spec)
                self._padx = padx
                self._pady = pady
                redraw = True
        if kw:
            super().configure(kw)  # type: ignore[arg-type]
        if redraw:
            self._redraw()
        return None

    config = configure
