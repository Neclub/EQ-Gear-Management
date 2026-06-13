"""Dark workbook styling for team gear Excel export."""

from __future__ import annotations

from openpyxl.styles import Font, PatternFill

# Base surfaces (sheet background)
FILL_SHEET = PatternFill("solid", fgColor="000000")
SHEET_BACKGROUND_ROWS = 50
SHEET_BACKGROUND_COLS = 26  # column Z
FILL_HEADER = PatternFill("solid", fgColor="2D2D32")
FILL_LABEL = PatternFill("solid", fgColor="252528")
FILL_ITEM_EMPTY = PatternFill("solid", fgColor="222226")

# Text
COLOR_TEXT = "E4E6EB"
COLOR_TEXT_MUTED = "A8ADB8"
COLOR_LINK = "8CB4FF"

FONT_HEADER = Font(name="Calibri", size=11, bold=True, color=COLOR_TEXT)
FONT_BODY = Font(name="Calibri", size=11, color=COLOR_TEXT)
FONT_LINK = Font(name="Calibri", size=11, color=COLOR_LINK, underline="single")
FONT_LEGEND_TITLE = Font(name="Calibri", size=11, bold=True, color=COLOR_TEXT)
FONT_LEGEND = Font(name="Calibri", size=10, color=COLOR_TEXT_MUTED)

# Gear-set fills (newest first) — muted tones for light text
GEAR_SET_FILLS: dict[str, str] = {
    "fracture": "3A3350",
    "shattered_dominion": "453040",
    "rebellion": "542A35",
    "bound": "4D3828",
    "eternal_reverie": "283850",
    "heroic_reflections": "264845",
    "spectral_luclinite": "2C4530",
    "spectral_luminosity": "3A4228",
    "luclinite_coagulated": "3A3935",
    "evolver": "5C4688",
}

EVOLVER_FILL = PatternFill("solid", fgColor=GEAR_SET_FILLS["evolver"])

# Missing Spells sheet
SPELL_BLOCK_HEADER_COLORS: dict[str, str] = {
    "121-125": "283850",
    "126-130": "3A3350",
}
SPELL_TIER_COLORS: dict[str, str] = {
    "Minor": "2A3545",
    "Lesser": "2E3A4C",
    "Median": "343C52",
    "Greater": "3A3850",
    "Glowing": "453848",
}
FILL_SPELL_DETAIL = PatternFill("solid", fgColor="1A1A1E")
FILL_SPELL_DETAIL_ALT = PatternFill("solid", fgColor="222228")
FILL_SPELL_COUNT = PatternFill("solid", fgColor="2E3340")
COLOR_TEXT_ACCENT = "F0F2F8"
FONT_COUNT = Font(name="Calibri", size=11, bold=True, color=COLOR_TEXT_ACCENT)
FONT_SECTION = Font(name="Calibri", size=13, bold=True, color=COLOR_TEXT)
FONT_BLOCK_HEADER = Font(name="Calibri", size=11, bold=True, color=COLOR_TEXT)
FONT_BLOCK_SUB = Font(name="Calibri", size=10, color=COLOR_TEXT_MUTED)


def gear_set_fill(key: str) -> PatternFill:
    return PatternFill("solid", fgColor=GEAR_SET_FILLS[key])


def spell_block_header_fill(block_label: str) -> PatternFill:
    color = SPELL_BLOCK_HEADER_COLORS.get(block_label, "2D2D32")
    return PatternFill("solid", fgColor=color)


def spell_tier_fill(tier: str) -> PatternFill:
    color = SPELL_TIER_COLORS.get(tier, "252528")
    return PatternFill("solid", fgColor=color)
