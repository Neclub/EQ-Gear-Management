"""Shared GUI color tokens (mockup 1 — calm unified layering)."""

from __future__ import annotations

# Window canvas, header, footer
BG = "#121214"

# Card shells (Team characters, Slots, Output)
BG_PANEL = "#24242c"

# Recessed insets (listbox, entry, combobox fields)
BG_RECESSED = "#0c0c10"

# Alias for input field backgrounds
BG_INPUT = BG_RECESSED

FG = "#e8eaef"
FG_MUTED = "#9ca3b4"

# Unified accent
ACCENT = "#5b8fd9"
ACCENT_FILES = ACCENT
ACCENT_SLOTS = ACCENT
ACCENT_OUTPUT = ACCENT
ACCENT_EXCEL = "#3d9b5c"

PANEL_BORDER = "#2e2e36"
INPUT_BORDER = "#454550"
BADGE_BG = "#35353d"
SCROLL_THUMB = "#454550"
SCROLL_THUMB_ACTIVE = "#5a5a68"

# Pill / chip helpers
GHOST_FILL = "#1a1a22"
GHOST_FILL_HOVER = "#2a2a32"
CHIP_ON_BG = "#35353d"
CHIP_OFF_BG = BG_RECESSED
CHIP_BORDER = INPUT_BORDER
