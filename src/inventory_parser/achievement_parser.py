"""Parse EverQuest /outputfile achievements dumps."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

EXPANSIONS_NEWEST_FIRST: tuple[tuple[str, int], ...] = (
    ("Shattering of Ro", 2025),
    ("The Outer Brood", 2024),
    ("Laurion's Song", 2023),
    ("Night of Shadows", 2022),
    ("Terror of Luclin", 2021),
    ("Claws of Veeshan", 2020),
    ("Torment of Velious", 2019),
    ("The Burning Lands", 2018),
    ("Ring of Scale", 2017),
    ("Empires of Kunark", 2016),
    ("The Broken Mirror", 2015),
    ("The Darkened Sea", 2014),
    ("Call of the Forsaken", 2013),
    ("Rain of Fear", 2012),
    ("Veil of Alaris", 2011),
    ("House of Thule", 2010),
    ("Underfoot", 2009),
    ("Seeds of Destruction", 2008),
    ("Secrets of Faydwer", 2007),
    ("The Buried Sea", 2007),
    ("The Serpent's Spine", 2006),
    ("Prophecy of Ro", 2006),
    ("Depths of Darkhollow", 2005),
    ("Dragons of Norrath", 2005),
    ("Omens of War", 2004),
    ("Gates of Discord", 2004),
    ("Lost Dungeons of Norrath", 2003),
    ("Legacy of Ykesha", 2003),
    ("Planes of Power", 2002),
    ("Shadows of Luclin", 2001),
    ("Scars of Velious", 2000),
    ("Ruins of Kunark", 2000),
)

_EXPANSION_ALIASES: dict[str, str] = {
    "the ruins of kunark": "Ruins of Kunark",
}

_EXTRA_KNOWN_EXPANSIONS = (
    "Anashti Sul",
    "Veeshan's Peak",
)

KNOWN_EXPANSIONS = tuple(
    name for name, _year in EXPANSIONS_NEWEST_FIRST
) + _EXTRA_KNOWN_EXPANSIONS + ("The Ruins of Kunark",)

EVERQUEST_BASE_LABEL = "EverQuest Original Release (1999)"

GENERAL_CATEGORIES = (
    "General",
    "Tradeskill",
    "Slayer",
    "Events",
    "Overseer",
    "The Hero's Journey",
    "EverQuest",
)

_STATUS_LINE = re.compile(r"^([CIL])\t")
_ZONE_SUFFIX = re.compile(r"^(.*)\s+\(([^)]+)\)\s*$")
_PROGRESS_SUFFIX = re.compile(r"^(.*)\t(\d+)/(\d+)\s*$")


@dataclass(frozen=True)
class MissingCollectionItem:
    section: str
    zone: str
    collection: str
    item: str
    owned: int
    total: int

    @property
    def progress(self) -> str:
        return f"{self.owned}/{self.total}"


@dataclass(frozen=True)
class SectionSummary:
    section: str
    completed: int
    incomplete: int

    @property
    def total(self) -> int:
        return self.completed + self.incomplete

    @property
    def completion_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round(100.0 * self.completed / self.total, 1)


@dataclass(frozen=True)
class MissingRaidAchievement:
    section: str
    raid: str
    objective: str


@dataclass
class AchievementParseResult:
    missing_collections: list[MissingCollectionItem] = field(default_factory=list)
    missing_raid_achievements: list[MissingRaidAchievement] = field(default_factory=list)
    section_summaries: list[SectionSummary] = field(default_factory=list)


def split_collection_name(name: str) -> tuple[str, str]:
    """``Eye Won! (Valley of King Xorbb)`` -> (collection, zone)."""
    match = _ZONE_SUFFIX.match(name.strip())
    if match is None:
        return name.strip(), ""
    return match.group(1).strip(), match.group(2).strip()


def _split_name_and_progress(text: str) -> tuple[str, int | None, int | None]:
    match = _PROGRESS_SUFFIX.match(text)
    if match is None:
        return text.strip(), None, None
    owned = int(match.group(2))
    total = int(match.group(3))
    return match.group(1).strip(), owned, total


def _parse_header_line(line: str) -> tuple[str, str, bool] | None:
    if _STATUS_LINE.match(line) or ":" not in line:
        return None
    name, subcategory = line.split(":", 1)
    section = name.strip()
    sub = subcategory.strip()
    if not section or not sub:
        return None
    if section in KNOWN_EXPANSIONS:
        return section, sub, True
    if section in GENERAL_CATEGORIES:
        return section, sub, False
    return section, sub, False


def _parse_status_line(line: str) -> tuple[str, str, int, int | None, int | None] | None:
    if not _STATUS_LINE.match(line):
        return None
    status = line[0]
    remaining = line[2:]
    indent = 0
    while remaining.startswith("\t"):
        indent += 1
        remaining = remaining[1:]
    name, owned, total = _split_name_and_progress(remaining)
    if not name:
        return None
    return status, name, indent, owned, total


def _is_collections_subcategory(subcategory: str) -> bool:
    return subcategory.casefold().endswith("collections")


def _is_raids_subcategory(subcategory: str) -> bool:
    return subcategory.casefold() == "raids"


def _is_missing_achievement_status(status: str) -> bool:
    return status in ("I", "L")


def _normalize_expansion_name(section: str) -> str:
    return _EXPANSION_ALIASES.get(section.casefold(), section)


def _expansion_year(section: str) -> int | None:
    normalized = _normalize_expansion_name(section)
    for name, year in EXPANSIONS_NEWEST_FIRST:
        if name == normalized:
            return year
    return None


def format_expansion_label(section: str) -> str:
    """Display label for expansion filters (newest expansions include release year)."""
    if section.casefold() == "everquest":
        return EVERQUEST_BASE_LABEL
    year = _expansion_year(section)
    if year is not None:
        return f"{_normalize_expansion_name(section)} ({year})"
    return section


def expansion_sort_key(section: str) -> tuple[int, str]:
    """Newest-to-oldest expansion order for Excel sorting and filters."""
    normalized = _normalize_expansion_name(section)
    for index, (name, _year) in enumerate(EXPANSIONS_NEWEST_FIRST):
        if name == normalized:
            return (index, section.casefold())
    if section.casefold() == "everquest":
        return (len(EXPANSIONS_NEWEST_FIRST), section.casefold())
    if section in GENERAL_CATEGORIES:
        return (len(EXPANSIONS_NEWEST_FIRST) + 1, section.casefold())
    return (len(EXPANSIONS_NEWEST_FIRST) + 2, section.casefold())


def parse_achievements_file(path: Path) -> AchievementParseResult:
    """Parse a ``Character_server-Achievements.txt`` dump."""
    current_section: str | None = None
    current_subcategory: str | None = None
    current_collection: str | None = None
    current_raid: str | None = None
    in_collections = False
    in_raids = False

    section_completed: dict[str, int] = {}
    section_incomplete: dict[str, int] = {}
    missing_collections: list[MissingCollectionItem] = []
    missing_raid_achievements: list[MissingRaidAchievement] = []

    with Path(path).open(encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n\r")
            if not line.strip():
                continue

            header = _parse_header_line(line)
            if header is not None:
                current_section, current_subcategory, _is_expansion = header
                current_collection = None
                current_raid = None
                in_collections = _is_collections_subcategory(current_subcategory)
                in_raids = _is_raids_subcategory(current_subcategory)
                continue

            parsed = _parse_status_line(line)
            if parsed is None or current_section is None:
                continue

            status, name, indent, owned, total = parsed

            if indent == 0:
                current_collection = name
                current_raid = name
                section_completed.setdefault(current_section, 0)
                section_incomplete.setdefault(current_section, 0)
                if status == "C":
                    section_completed[current_section] += 1
                else:
                    section_incomplete[current_section] += 1
                continue

            if in_raids and _is_missing_achievement_status(status) and current_raid is not None:
                missing_raid_achievements.append(
                    MissingRaidAchievement(
                        section=current_section,
                        raid=current_raid,
                        objective=name,
                    )
                )

            if not in_collections or current_collection is None:
                continue
            if status != "I" or owned is None or total is None or owned >= total:
                continue

            collection_name, zone = split_collection_name(current_collection)
            missing_collections.append(
                MissingCollectionItem(
                    section=current_section,
                    zone=zone,
                    collection=collection_name,
                    item=name,
                    owned=owned,
                    total=total,
                )
            )

    summaries = [
        SectionSummary(
            section=section,
            completed=section_completed.get(section, 0),
            incomplete=section_incomplete.get(section, 0),
        )
        for section in sorted(
            set(section_completed) | set(section_incomplete),
            key=str.casefold,
        )
    ]
    return AchievementParseResult(
        missing_collections=missing_collections,
        missing_raid_achievements=missing_raid_achievements,
        section_summaries=summaries,
    )
