"""Build Raid BiS export data from a parsed team gear report."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from inventory_parser.output_paths import default_export_prefix_from_report
from inventory_parser.raid_bis.catalog import fetch_catalog
from inventory_parser.raid_bis.compare import (
    CharacterRaidBis,
    compare_character,
    resolve_equipped_stats,
)
from inventory_parser.raid_bis.models import RaidBisCatalog
from inventory_parser.slot2_augs.build import report_progress
from inventory_parser.team_report import TeamGearReport

ProgressFn = Callable[[dict], None]


@dataclass
class RaidBisExport:
    catalog: RaidBisCatalog
    characters: list[CharacterRaidBis] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    export_prefix: str = "Team"
    icon_data_uris: dict[str, str] = field(default_factory=dict)


def build_raid_bis_export(
    team: TeamGearReport,
    *,
    on_progress: ProgressFn | None = None,
    allow_network: bool = True,
    html_overrides: dict[str, str] | None = None,
    item_html_by_id: dict[int, str] | None = None,
    hydrate: bool = True,
    embed_icons: bool = True,
) -> RaidBisExport:
    """Fetch the raid catalog and compare each character's equipped gear."""
    warnings: list[str] = []
    report_progress(on_progress, "Fetching current-expansion raid gear catalog…", 0.0, 0.35, 0, 1)
    catalog = fetch_catalog(
        allow_network=allow_network,
        html_overrides=html_overrides,
        item_html_by_id=item_html_by_id,
        hydrate=hydrate,
    )
    report_progress(on_progress, "Fetching current-expansion raid gear catalog…", 0.0, 0.35, 1, 1)
    if catalog.warning:
        warnings.append(catalog.warning)

    report_progress(on_progress, "Comparing equipped gear to Raid BiS…", 0.35, 0.85, 0, 1)
    equipped = resolve_equipped_stats(
        team.characters,
        catalog.items,
        item_html_by_id=item_html_by_id,
        allow_network=allow_network and not html_overrides,
    )
    characters: list[CharacterRaidBis] = []
    n = max(len(team.characters), 1)
    for i, ch in enumerate(team.characters, start=1):
        characters.append(
            compare_character(ch, catalog.items, equipped_stats=equipped)
        )
        report_progress(
            on_progress,
            f"Comparing equipped gear to Raid BiS… ({i}/{len(team.characters)})",
            0.35,
            0.85,
            i,
            n,
        )

    icon_data_uris: dict[str, str] = {}
    if embed_icons:
        from inventory_parser.raid_bis.icons import collect_icon_data_uris

        icon_ids = set()
        for ch in characters:
            for slot in ch.slots:
                if slot.recommended_icon_id:
                    icon_ids.add(slot.recommended_icon_id)
                if slot.current_icon_id:
                    icon_ids.add(slot.current_icon_id)
        icon_data_uris = collect_icon_data_uris(
            icon_ids,
            allow_network=allow_network and not html_overrides,
        )

    prefix = default_export_prefix_from_report(team)
    return RaidBisExport(
        catalog=catalog,
        characters=characters,
        warnings=warnings,
        export_prefix=prefix,
        icon_data_uris=icon_data_uris,
    )
