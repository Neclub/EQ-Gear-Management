"""Pill-shaped tkinter button with variant colors matching the GUI theme."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageDraw, ImageTk

from inventory_parser.gui_theme import (
    ACCENT as _ACCENT_CHIP,
    ACCENT_EXCEL as _ACCENT_EXCEL,
    BG as _FALLBACK_BG,
    BG_PANEL as _BG_PANEL,
    BG_RECESSED as _BG_RECESSED,
    CHIP_BORDER as _CHIP_BORDER,
    CHIP_OFF_BG as _CHIP_OFF_BG,
    CHIP_ON_BG as _CHIP_ON_BG,
    FG as _FG,
    FG_MUTED as _FG_MUTED,
    GHOST_FILL as _GHOST_FILL,
    GHOST_FILL_HOVER as _GHOST_FILL_HOVER,
    INPUT_BORDER as _INPUT_BORDER,
    SCROLL_THUMB as _SCROLL_THUMB,
)

_AA_SCALE = 3
_ACCENT_EXCEL_ACTIVE = "#2f7a47"
_ACCENT_DANGER = "#c45c5c"
_ACCENT_DANGER_ACTIVE = "#a04848"

_ACCENT_PRIMARY = "#3d6fad"
_ACCENT_PRIMARY_HOVER = "#4a7ec4"
_ACCENT_SECONDARY = "#2a8a8f"
_ACCENT_SECONDARY_HOVER = "#3d9994"

_VARIANT_PADDING: dict[str, tuple[tuple[int, int], tuple[str, int, str] | tuple[str, int]]] = {
    "default": ((10, 6), ("Segoe UI", 10)),
    "primary": ((10, 6), ("Segoe UI", 10)),
    "secondary": ((10, 6), ("Segoe UI", 10)),
    "danger": ((10, 6), ("Segoe UI", 10)),
    "accent": ((18, 11), ("Segoe UI", 11, "bold")),
    "ghost": ((8, 5), ("Segoe UI", 9)),
    "compact": ((10, 6), ("Segoe UI", 10)),
}


@dataclass(frozen=True)
class _PillColors:
    fill: str
    fill_hover: str
    fill_disabled: str
    fg: str
    fg_disabled: str


_VARIANTS: dict[str, _PillColors] = {
    "default": _PillColors(_CHIP_ON_BG, _SCROLL_THUMB, _GHOST_FILL, _FG, _FG_MUTED),
    "primary": _PillColors(_ACCENT_PRIMARY, _ACCENT_PRIMARY_HOVER, _BG_RECESSED, "#ffffff", _FG_MUTED),
    "secondary": _PillColors(_ACCENT_SECONDARY, _ACCENT_SECONDARY_HOVER, _BG_RECESSED, "#ffffff", _FG_MUTED),
    "danger": _PillColors(_ACCENT_DANGER, _ACCENT_DANGER_ACTIVE, _BG_RECESSED, "#ffffff", _FG_MUTED),
    "accent": _PillColors(_ACCENT_EXCEL, _ACCENT_EXCEL_ACTIVE, _BG_RECESSED, "#ffffff", _FG_MUTED),
    "ghost": _PillColors(_GHOST_FILL, _GHOST_FILL_HOVER, _BG_PANEL, _FG, _FG_MUTED),
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


def _render_rounded_chip_rgba(
    width: int,
    height: int,
    *,
    fill: str,
    outline: str | None = None,
    outline_width: int = 1,
    radius: int = 10,
) -> Image.Image:
    """Anti-aliased rounded chip (toggle buttons)."""
    scale = _AA_SCALE
    src_w = max(width * scale, 1)
    src_h = max(height * scale, 1)
    src_radius = max(min(radius, height // 2) * scale, 0)
    src_outline = max(outline_width * scale, 0)
    image = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    box = (0, 0, src_w - 1, src_h - 1)
    if outline and src_outline > 0:
        draw.rounded_rectangle(
            box,
            radius=src_radius,
            fill=_hex_to_rgba(fill),
            outline=_hex_to_rgba(outline),
            width=src_outline,
        )
    else:
        draw.rounded_rectangle(box, radius=src_radius, fill=_hex_to_rgba(fill))
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
        width: int | None = None,
        icon: str = "",
        **kwargs: object,
    ) -> None:
        bg = _parent_bg(parent)
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0)
        self._icon = icon
        self._text = text
        self._command = command
        self._variant = variant if variant in _VARIANTS else "default"
        self._state = tk.NORMAL
        self._hover = False
        self._fixed_width = width
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
        label = f"{self._icon} {self._text}".strip() if self._icon else self._text
        text_w = self._font.measure(label)
        width = self._fixed_width if self._fixed_width else max(text_w + self._padx * 2, self._pady * 4)
        height = self._font.metrics("linespace") + self._pady * 2

        self._canvas.configure(width=width, height=height)
        super().configure(width=width, height=height)

        fill = self._fill_color()
        rgba = _render_pill_rgba(width, height, fill)
        try:
            self._pill_image = ImageTk.PhotoImage(rgba, name=self._image_name, master=self)
        finally:
            rgba.close()
        self._canvas.create_image(width // 2, height // 2, image=self._pill_image)
        label = f"{self._icon} {self._text}".strip() if self._icon else self._text
        self._canvas.create_text(
            width // 2,
            height // 2,
            text=label,
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
        if "icon" in kw:
            self._icon = str(kw.pop("icon"))
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
        if "width" in kw:
            self._fixed_width = kw.pop("width")  # type: ignore[assignment]
            redraw = True
        if kw:
            super().configure(kw)  # type: ignore[arg-type]
        if redraw:
            self._redraw()
        return None

    config = configure


class ChipToggle(tk.Frame):
    """Horizontal toggle chip for export options (Spells / Achievements / HTML)."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        variable: tk.BooleanVar,
        *,
        icon: str = "",
        command: Callable[[], None] | None = None,
    ) -> None:
        bg = _parent_bg(parent)
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0)
        self._variable = variable
        self._command = command
        self._state = tk.NORMAL
        self._icon = icon
        self._label = text
        self._hover = False
        self._chip_image: ImageTk.PhotoImage | None = None
        self._chip_image_name = f"inventory_parser_chip_{id(self)}"

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self._canvas.pack()

        for widget in (self, self._canvas):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

        self._variable.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _enabled(self) -> bool:
        return self._state != tk.DISABLED

    def _on_enter(self, _event: tk.Event) -> None:
        if not self._enabled():
            return
        self._hover = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._redraw()

    def _on_click(self, _event: tk.Event) -> None:
        if not self._enabled():
            return
        self._variable.set(not self._variable.get())
        if self._command:
            self._command()

    def _redraw(self) -> None:
        parent_bg = _parent_bg(self)
        self._release_chip_image()
        self._canvas.delete("all")
        font = tkfont.Font(family="Segoe UI", size=9)
        on = self._variable.get() and self._enabled()
        if on:
            fill = _ACCENT_CHIP if self._enabled() else _BG_PANEL
        elif self._enabled():
            fill = _CHIP_OFF_BG if not self._hover else _GHOST_FILL_HOVER
        else:
            fill = _BG_PANEL
        outline = _ACCENT_CHIP if on else _CHIP_BORDER
        mark = " ✓" if on else ""
        display = f"{self._icon} {self._label}{mark}".strip()
        text_w = font.measure(display)
        width = max(text_w + 24, 80)
        height = font.metrics("linespace") + 14

        self._canvas.configure(width=width, height=height, bg=parent_bg)
        self.configure(width=width, height=height)

        chip_rgba = _render_rounded_chip_rgba(
            width,
            height,
            fill=fill,
            outline=outline,
            outline_width=1,
            radius=10,
        )
        try:
            self._chip_image = ImageTk.PhotoImage(chip_rgba, name=self._chip_image_name, master=self)
        finally:
            chip_rgba.close()
        self._canvas.create_image(width // 2, height // 2, image=self._chip_image)
        fg = "#ffffff" if on and self._enabled() else (_FG if self._enabled() else _FG_MUTED)
        self._canvas.create_text(width // 2, height // 2, text=display, fill=fg, font=font)
        self._canvas.configure(cursor="hand2" if self._enabled() else "")

    def _release_chip_image(self) -> None:
        self._chip_image = None
        try:
            self.tk.call("image", "delete", self._chip_image_name)
        except tk.TclError:
            pass

    def configure(self, cnf: dict[str, object] | None = None, **kw: object) -> dict[str, object] | None:
        if cnf:
            kw = {**cnf, **kw}
        redraw = False
        if "state" in kw:
            self._state = str(kw.pop("state"))
            redraw = True
        if kw:
            super().configure(kw)  # type: ignore[arg-type]
        if redraw:
            self._redraw()
        return None

    config = configure


class PillBadge(tk.Frame):
    """Small pill-shaped version or status badge."""

    def __init__(self, parent: tk.Misc, text: str) -> None:
        bg = _parent_bg(parent)
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0)
        font = tkfont.Font(family="Segoe UI", size=8)
        text_w = font.measure(text)
        width = max(text_w + 14, 36)
        height = font.metrics("linespace") + 6
        image_name = f"inventory_parser_badge_{id(self)}"
        rgba = _render_pill_rgba(width, height, _CHIP_ON_BG)
        try:
            photo = ImageTk.PhotoImage(rgba, name=image_name, master=self)
        finally:
            rgba.close()
        canvas = tk.Canvas(self, width=width, height=height, bg=bg, highlightthickness=0, bd=0)
        canvas.pack()
        canvas.create_image(width // 2, height // 2, image=photo)
        canvas.create_text(width // 2, height // 2, text=text, fill=_FG_MUTED, font=font)
        self._badge_photo = photo
        self.configure(width=width, height=height)
