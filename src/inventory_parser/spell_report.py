"""Build missing Rank III spell / rune reports."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from inventory_parser.team_report import TeamGearReport
from inventory_parser.missing_spells import (
    MissingSpellLine,
    counts_as_missing_rk3,
    discover_missing_spells_for_inventories,
    is_missing_rank_iii,
    normalize_spell_rank_iii,
    parse_missing_spells_file,
    spell_path_for_persona,
    strip_spell_rank,
)
from inventory_parser.spell_runes import (
    MissingRuneExpansionGroup,
    SpellLevelBlock,
    block_for_level,
    enabled_blocks,
    load_rune_config,
    missing_rune_expansion_groups,
    rune_tier_for_level,
)
from inventory_parser.spell_catalog import lookup_expansion_label


@dataclass(frozen=True)
class MissingRankIII:
    persona_key: str
    display_name: str
    character: str
    level: int
    spell_name: str
    block_label: str
    rune_tier: str
    turn_in_theme: str
    expansion: str = ""


@dataclass
class SpellRuneReport:
    persona_keys: list[str]
    entries: list[MissingRankIII] = field(default_factory=list)
    counts_by_persona: dict[str, dict[str, dict[str, int]]] = field(default_factory=dict)
    blocks: tuple[SpellLevelBlock, ...] = ()
    expansion_groups: tuple[MissingRuneExpansionGroup, ...] = ()
    warnings: list[str] = field(default_factory=list)

    @property
    def counts_by_character(self) -> dict[str, dict[str, dict[str, int]]]:
        """Backward-compatible alias for :attr:`counts_by_persona`."""
        return self.counts_by_persona

    @property
    def characters(self) -> list[str]:
        """Backward-compatible alias for :attr:`persona_keys`."""
        return self.persona_keys


def _spell_personas(team: TeamGearReport) -> list:
    if team.spell_characters:
        return team.spell_characters
    return team.characters


def build_spell_rune_report(
    team: TeamGearReport,
    spell_paths: dict[str, Path] | None = None,
    *,
    inventory_paths: list[Path] | None = None,
    extra_spell_paths: list[Path] | None = None,
    discovery_warnings: list[str] | None = None,
) -> SpellRuneReport | None:
    """
    Build spell rune data for team characters.

    If ``spell_paths`` is omitted, discovers files from ``inventory_paths``,
    ``extra_spell_paths``, or each character's inventory filepath.
    """
    config = load_rune_config()
    blocks = enabled_blocks(config)
    if not blocks:
        return None

    personas = _spell_personas(team)
    warnings: list[str] = list(discovery_warnings or [])
    if spell_paths is None:
        inv_paths = inventory_paths or [Path(c.filepath) for c in personas]
        discovery = discover_missing_spells_for_inventories(
            inv_paths,
            extra_spell_paths=extra_spell_paths,
        )
        spell_paths = discovery.paths
        warnings.extend(discovery.warnings)

    if not spell_paths:
        return None

    persona_order = [c.persona_key for c in personas]
    report = SpellRuneReport(
        persona_keys=persona_order,
        blocks=blocks,
        expansion_groups=missing_rune_expansion_groups(),
        warnings=warnings,
    )
    counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )

    for char_gear in personas:
        pk = char_gear.persona_key
        spell_path = spell_path_for_persona(
            char_gear.character,
            char_gear.server,
            char_gear.class_abbr,
            spell_paths,
        )
        if spell_path is None:
            suffix = f"-{char_gear.class_abbr}" if char_gear.class_abbr else ""
            report.warnings.append(
                f"No MissingSpells file for {char_gear.display_name} "
                f"(expected {char_gear.character}_{char_gear.server}{suffix}-*-MissingSpells.txt)"
            )
            continue

        candidates: dict[tuple[int, str], MissingSpellLine] = {}
        for line in parse_missing_spells_file(spell_path):
            if not counts_as_missing_rk3(line.name):
                continue
            tier = rune_tier_for_level(line.level, config)
            if tier is None:
                continue
            dedupe_key = (line.level, strip_spell_rank(line.name).casefold())
            existing = candidates.get(dedupe_key)
            if existing is None or (
                is_missing_rank_iii(line.name)
                and not is_missing_rank_iii(existing.name)
            ):
                candidates[dedupe_key] = line

        for line in candidates.values():
            tier = rune_tier_for_level(line.level, config)
            assert tier is not None
            block = block_for_level(line.level, config)
            assert block is not None
            entry = MissingRankIII(
                persona_key=pk,
                display_name=char_gear.display_name,
                character=char_gear.character,
                level=line.level,
                spell_name=normalize_spell_rank_iii(line.name),
                block_label=block.label,
                rune_tier=tier,
                turn_in_theme=block.turn_in_theme,
                expansion=lookup_expansion_label(
                    char_gear.class_abbr,
                    line.level,
                    normalize_spell_rank_iii(line.name),
                ),
            )
            report.entries.append(entry)
            if entry.expansion:
                counts[pk][entry.expansion][tier] += 1

    report.entries.sort(
        key=lambda e: (
            e.persona_key.casefold(),
            e.expansion.casefold(),
            e.level,
            e.spell_name.casefold(),
        )
    )
    report.counts_by_persona = {
        pk: {label: dict(tiers) for label, tiers in by_block.items()}
        for pk, by_block in counts.items()
    }
    for pk in persona_order:
        report.counts_by_persona.setdefault(pk, {})

    return report
