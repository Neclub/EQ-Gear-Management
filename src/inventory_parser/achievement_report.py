"""Build achievement collection and summary reports for team exports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from inventory_parser.achievement_files import collect_achievement_paths
from inventory_parser.achievement_parser import (
    AchievementParseResult,
    MissingCollectionItem,
    MissingRaidAchievement,
    SectionSummary,
    expansion_sort_key,
    parse_achievements_file,
)
from inventory_parser.team_report import TeamGearReport
from inventory_parser.parser import parse_inventory_file


@dataclass(frozen=True)
class MissingCollectionRow:
    character: str
    expansion: str
    zone: str
    collection: str
    missing_item: str
    progress: str
    char_has: str
    total: int


@dataclass(frozen=True)
class AchievementSummaryRow:
    character: str
    section: str
    completed: int
    incomplete: int
    total: int
    completion_pct: float


@dataclass(frozen=True)
class RaidAchievementRow:
    character: str
    expansion: str
    raid: str
    objective: str


@dataclass
class AchievementReport:
    missing_collections: list[MissingCollectionRow] = field(default_factory=list)
    raid_achievements: list[RaidAchievementRow] = field(default_factory=list)
    summaries: list[AchievementSummaryRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        return bool(self.missing_collections or self.raid_achievements or self.summaries)


def _character_key(character: str, server: str) -> str:
    return f"{character}_{server}".casefold()


def _build_item_holders_by_name(team: TeamGearReport) -> dict[str, list[str]]:
    """Map item name (casefold) to team display names that have it in inventory."""
    holders: dict[str, list[str]] = {}
    seen: dict[str, set[str]] = {}
    for character in team.characters:
        data = parse_inventory_file(character.filepath)
        if data is None:
            continue
        for item in data.items:
            if not item.name or item.name == "Empty":
                continue
            key = item.name.casefold()
            seen_names = seen.setdefault(key, set())
            if character.display_name in seen_names:
                continue
            seen_names.add(character.display_name)
            holders.setdefault(key, []).append(character.display_name)
    for names in holders.values():
        names.sort(key=str.casefold)
    return holders


def _char_has_item(item_name: str, holders: dict[str, list[str]]) -> str:
    names = holders.get(item_name.casefold(), [])
    return ", ".join(names)


def _raid_rows_from_parse(
    display_name: str,
    raids: list[MissingRaidAchievement],
) -> list[RaidAchievementRow]:
    return [
        RaidAchievementRow(
            character=display_name,
            expansion=raid.section,
            raid=raid.raid,
            objective=raid.objective,
        )
        for raid in raids
    ]


def _sort_missing_collection_rows(rows: list[MissingCollectionRow]) -> list[MissingCollectionRow]:
    return sorted(
        rows,
        key=lambda row: (
            expansion_sort_key(row.expansion),
            row.zone.casefold(),
            row.collection.casefold(),
            row.missing_item.casefold(),
            row.character.casefold(),
        ),
    )


def _sort_achievement_summary_rows(rows: list[AchievementSummaryRow]) -> list[AchievementSummaryRow]:
    return sorted(
        rows,
        key=lambda row: (
            expansion_sort_key(row.section),
            row.character.casefold(),
        ),
    )


def _sort_raid_achievement_rows(rows: list[RaidAchievementRow]) -> list[RaidAchievementRow]:
    return sorted(
        rows,
        key=lambda row: (
            expansion_sort_key(row.expansion),
            row.raid.casefold(),
            row.objective.casefold(),
            row.character.casefold(),
        ),
    )


def _rows_from_parse(
    display_name: str,
    parsed: AchievementParseResult,
    item_holders: dict[str, list[str]],
) -> tuple[list[MissingCollectionRow], list[RaidAchievementRow], list[AchievementSummaryRow]]:
    missing = [
        MissingCollectionRow(
            character=display_name,
            expansion=item.section,
            zone=item.zone,
            collection=item.collection,
            missing_item=item.item,
            progress=item.progress,
            char_has=_char_has_item(item.item, item_holders),
            total=item.total,
        )
        for item in parsed.missing_collections
    ]
    summaries = [
        AchievementSummaryRow(
            character=display_name,
            section=summary.section,
            completed=summary.completed,
            incomplete=summary.incomplete,
            total=summary.total,
            completion_pct=summary.completion_pct,
        )
        for summary in parsed.section_summaries
        if summary.total > 0
    ]
    raids = _raid_rows_from_parse(display_name, parsed.missing_raid_achievements)
    return missing, raids, summaries


def build_achievement_report(
    team: TeamGearReport,
    achievement_paths: dict[str, Path] | None = None,
    *,
    inventory_paths: list[Path] | None = None,
    extra_achievement_paths: list[Path] | None = None,
) -> AchievementReport | None:
    """Build achievement rows for characters with achievement dumps."""
    if achievement_paths is None:
        if not inventory_paths and not extra_achievement_paths:
            inventory_paths = [Path(c.filepath) for c in team.characters]
        achievement_paths = collect_achievement_paths(
            inventory_paths or [],
            extra_achievement_paths,
        )
    if not achievement_paths:
        return None

    report = AchievementReport()
    seen_characters: set[str] = set()
    item_holders = _build_item_holders_by_name(team)

    for character in team.characters:
        key = _character_key(character.character, character.server)
        path = achievement_paths.get(key)
        if path is None:
            continue
        seen_characters.add(key)
        try:
            parsed = parse_achievements_file(path)
        except OSError as exc:
            report.warnings.append(
                f"Could not read achievements for {character.display_name}: {exc}"
            )
            continue
        missing, raids, summaries = _rows_from_parse(
            character.display_name,
            parsed,
            item_holders,
        )
        report.missing_collections.extend(missing)
        report.raid_achievements.extend(raids)
        report.summaries.extend(summaries)

    report.raid_achievements = _sort_raid_achievement_rows(report.raid_achievements)
    report.missing_collections = _sort_missing_collection_rows(report.missing_collections)
    report.summaries = _sort_achievement_summary_rows(report.summaries)

    for key, path in achievement_paths.items():
        if key in seen_characters:
            continue
        report.warnings.append(
            f"Achievement file has no matching inventory character: {path.name}"
        )

    if not report.has_data and not report.warnings:
        return None
    return report
