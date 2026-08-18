"""Serialize Raid BiS for the HTML team report section."""

from __future__ import annotations

from inventory_parser import __version__
from inventory_parser.items import EQRESOURCE_ITEM_URL
from inventory_parser.raid_bis.build import RaidBisExport
from inventory_parser.raid_bis.compare import format_stat_deltas
from inventory_parser.slot2_augs.html import format_catalog_fetched_at


def serialize_raid_bis_section(bundle: RaidBisExport) -> dict:
    characters: list[dict] = []
    for ch in bundle.characters:
        characters.append(
            {
                "character": ch.character,
                "server": ch.server,
                "classAbbr": ch.class_abbr,
                "displayName": ch.display_name,
                "personaKey": ch.persona_key,
                "slotsChanged": ch.slots_changed,
                "totalDeltas": dict(ch.total_deltas),
                "totalDeltaText": format_stat_deltas(
                    ch.total_deltas, class_abbr=ch.class_abbr
                ),
                "slots": [
                    {
                        "gearSlot": s.gear_slot,
                        "status": s.status,
                        "currentName": s.current_name,
                        "currentId": s.current_id,
                        "recommendedName": s.recommended_name,
                        "recommendedId": s.recommended_id,
                        "recommendedTier": s.recommended_tier,
                        "recommendedIconId": s.recommended_icon_id,
                        "currentIconId": s.current_icon_id,
                        "deltas": dict(s.deltas),
                        "deltaText": format_stat_deltas(
                            s.deltas, class_abbr=ch.class_abbr
                        ),
                        "note": s.note,
                        "petFocus": s.pet_focus,
                        "scored": s.scored,
                    }
                    for s in ch.slots
                ],
            }
        )

    title_name = (bundle.export_prefix or "").strip() or "EQ"
    if len(bundle.characters) == 1:
        ch = bundle.characters[0]
        title_name = (ch.character or title_name).strip()
        if ch.class_abbr:
            title_name = f"{title_name} - {ch.class_abbr}"

    return {
        "reportTitle": f"{title_name} Raid BiS",
        "appVersion": __version__,
        "warnings": bundle.warnings,
        "catalogFetchedAt": format_catalog_fetched_at(bundle.catalog.fetched_at),
        "catalogFromCache": bundle.catalog.from_cache,
        "eqResourceItemUrl": EQRESOURCE_ITEM_URL,
        "iconDataUris": bundle.icon_data_uris,
        "characters": characters,
    }
