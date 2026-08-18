"""Score current-expansion raid gear against equipped items using aug weights."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping

from inventory_parser.items import EquippedItem
from inventory_parser.raid_bis.catalog import hydrate_item_ids
from inventory_parser.raid_bis.models import (
    NON_LORE_SLOTS,
    PAPERDOLL_SLOTS,
    PET_FOCUS_CLASSES,
    SCORED_SLOTS,
    UNSCORED_SLOTS,
    RaidGearCandidate,
    slot_base,
)
from inventory_parser.slot2_augs.aug_stats import STAT_DISPLAY, STAT_KEYS
from inventory_parser.slot2_augs.profiles import CLASS_TO_PROFILE, PROFILE_FOCUS_STAT
from inventory_parser.slot2_augs.weights import resolve_weights
from inventory_parser.team_report import CharacterGear

SlotStatus = Literal["empty", "bis", "upgrade", "unknown", "weapon"]

DELTA_STAT_ORDER: tuple[str, ...] = (
    "ac",
    "hp",
    "mana",
    "endurance",
    "hdex",
    "hint",
    "hwis",
    "hstr",
    "hsta",
    "hagi",
    "hcha",
    "atk",
    "spell_damage",
    "heal_amount",
    "clairvoyance",
)


def score_stats(stats: Mapping[str, int] | None, weights: Mapping[str, float]) -> float:
    data = stats or {}
    total = 0.0
    for key, weight in weights.items():
        total += float(data.get(key, 0)) * float(weight)
    return total


def rank_tuple(
    item: RaidGearCandidate,
    class_abbr: str | None,
    gear_slot: str,
) -> tuple:
    weights = resolve_weights(class_abbr, gear_slot)
    score = score_stats(item.stats, weights)
    hp = int(item.stats.get("hp", 0))
    ac = int(item.stats.get("ac", 0))
    return (-score, -hp, -ac, item.name.casefold())


def legal_for_slot(
    item: RaidGearCandidate,
    *,
    class_abbr: str | None,
    gear_slot: str,
) -> bool:
    return item.fits_class(class_abbr) and item.fits_slot(gear_slot)


def _best(
    candidates: list[RaidGearCandidate],
    *,
    class_abbr: str | None,
    gear_slot: str,
    used: set[str],
) -> RaidGearCandidate | None:
    legal = [
        c
        for c in candidates
        if legal_for_slot(c, class_abbr=class_abbr, gear_slot=gear_slot)
        and c.lore_key() not in used
    ]
    if not legal:
        return None
    legal.sort(key=lambda c: rank_tuple(c, class_abbr, gear_slot))
    return legal[0]


def build_ideal_loadout(
    catalog: list[RaidGearCandidate],
    *,
    class_abbr: str | None,
    equipped: dict[str, EquippedItem] | None = None,
) -> dict[str, RaidGearCandidate]:
    """Best unique item per scored slot, with MAG/BST/NEC pet-focus ear pinned."""
    equipped = equipped or {}
    used: set[str] = set()
    loadout: dict[str, RaidGearCandidate] = {}
    class_key = (class_abbr or "").strip().upper() or None

    if class_key in PET_FOCUS_CLASSES:
        pin_slot, pin_item = _choose_pet_focus_ear(
            catalog, class_abbr=class_key, equipped=equipped
        )
        if pin_slot and pin_item:
            loadout[pin_slot] = pin_item
            used.add(pin_item.lore_key())

    for slot in SCORED_SLOTS:
        if slot in loadout:
            continue
        slot_used = set() if slot in NON_LORE_SLOTS else used
        pick = _best(catalog, class_abbr=class_key, gear_slot=slot, used=slot_used)
        if pick is None:
            continue
        loadout[slot] = pick
        if slot not in NON_LORE_SLOTS:
            used.add(pick.lore_key())
    return loadout


def _choose_pet_focus_ear(
    catalog: list[RaidGearCandidate],
    *,
    class_abbr: str,
    equipped: dict[str, EquippedItem],
) -> tuple[str | None, RaidGearCandidate | None]:
    ears = [
        c
        for c in catalog
        if c.is_pet_focus_ear()
        and legal_for_slot(c, class_abbr=class_abbr, gear_slot="Ear-1")
    ]
    if not ears:
        return None, None
    ears.sort(key=lambda c: rank_tuple(c, class_abbr, "Ear-1"))
    best = ears[0]

    worn_slots = []
    for slot in ("Ear-1", "Ear-2"):
        cur = equipped.get(slot)
        if cur is None or cur.item_id <= 0:
            continue
        match = next((c for c in ears if c.item_id == cur.item_id), None)
        if match is None and (
            "summoner" in cur.name.casefold()
            or any(
                c.name.casefold() == cur.name.casefold() and c.is_pet_focus_ear()
                for c in catalog
            )
        ):
            match = next(
                (c for c in catalog if c.item_id == cur.item_id and c.is_pet_focus_ear()),
                None,
            )
        if match is not None or "summoner" in cur.name.casefold():
            worn_slots.append(slot)

    pin_slot = worn_slots[0] if worn_slots else "Ear-1"
    return pin_slot, best


def stat_deltas(
    current: Mapping[str, int] | None,
    recommended: Mapping[str, int] | None,
) -> dict[str, int]:
    left = current or {}
    right = recommended or {}
    keys = [k for k in DELTA_STAT_ORDER if k in STAT_KEYS]
    extra = [k for k in STAT_KEYS if k not in keys]
    out: dict[str, int] = {}
    for key in keys + extra:
        delta = int(right.get(key, 0)) - int(left.get(key, 0))
        if delta:
            out[key] = delta
    return out


def display_delta_keys(class_abbr: str | None) -> tuple[str, ...]:
    """HP, Mana, primary HStat, and Spell Damage for casters."""
    keys: list[str] = ["hp", "mana"]
    profile = CLASS_TO_PROFILE.get((class_abbr or "").strip().upper())
    if profile:
        keys.append(PROFILE_FOCUS_STAT[profile])
    if profile in {"int", "wis"}:
        keys.append("spell_damage")
    return tuple(keys)


def format_stat_deltas(
    deltas: Mapping[str, int],
    class_abbr: str | None = None,
) -> str:
    parts: list[str] = []
    for key in display_delta_keys(class_abbr):
        if key not in deltas:
            continue
        value = int(deltas[key])
        label = STAT_DISPLAY.get(key, key)
        parts.append(f"{value:+d} {label}")
    return ", ".join(parts)


def sum_deltas(rows: list[dict[str, int]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            totals[key] = totals.get(key, 0) + int(value)
    return {k: v for k, v in totals.items() if v}


@dataclass
class SlotComparison:
    gear_slot: str
    status: SlotStatus
    current_name: str | None = None
    current_id: int | None = None
    recommended_name: str | None = None
    recommended_id: int | None = None
    recommended_tier: str = ""
    recommended_icon_id: str | None = None
    current_icon_id: str | None = None
    deltas: dict[str, int] = field(default_factory=dict)
    note: str = ""
    pet_focus: bool = False
    scored: bool = True


@dataclass
class CharacterRaidBis:
    character: str
    server: str
    class_abbr: str | None
    display_name: str
    persona_key: str
    slots: list[SlotComparison] = field(default_factory=list)
    total_deltas: dict[str, int] = field(default_factory=dict)
    slots_changed: int = 0


def compare_character(
    character: CharacterGear,
    catalog: list[RaidGearCandidate],
    *,
    equipped_stats: dict[int, RaidGearCandidate] | None = None,
) -> CharacterRaidBis:
    equipped_stats = equipped_stats or {}
    class_abbr = (character.class_abbr or "").strip().upper() or None
    loadout = build_ideal_loadout(
        catalog, class_abbr=class_abbr, equipped=character.slots
    )
    by_id = {c.item_id: c for c in catalog if c.item_id > 0}
    rows: list[SlotComparison] = []
    delta_rows: list[dict[str, int]] = []
    changed = 0

    for slot in PAPERDOLL_SLOTS:
        current = character.slots.get(slot)
        if slot in UNSCORED_SLOTS:
            note = (
                "Power Source is not scored."
                if slot == "Power Source"
                else "Weapons are not scored yet."
            )
            current_icon = None
            if current and current.item_id > 0:
                known = by_id.get(current.item_id) or equipped_stats.get(current.item_id)
                if known:
                    current_icon = known.icon_id
            rows.append(
                SlotComparison(
                    gear_slot=slot,
                    status="weapon",
                    current_name=current.name if current else None,
                    current_id=current.item_id if current else None,
                    current_icon_id=current_icon,
                    note=note,
                    scored=False,
                )
            )
            continue

        recommended = loadout.get(slot)
        current_stats: dict[str, int] = {}
        current_icon = None
        if current and current.item_id > 0:
            known = by_id.get(current.item_id) or equipped_stats.get(current.item_id)
            if known:
                current_stats = dict(known.stats)
                current_icon = known.icon_id

        rec_stats = dict(recommended.stats) if recommended else {}
        deltas = stat_deltas(current_stats, rec_stats) if recommended else {}
        pet_focus = bool(recommended and recommended.is_pet_focus_ear() and slot_base(slot) == "Ear")

        if recommended is None:
            status: SlotStatus = "unknown"
            note = "No current-expansion raid item found for this slot/class."
        elif current is None or current.item_id <= 0:
            status = "empty"
            note = "No item equipped."
            changed += 1
            delta_rows.append(deltas)
        elif current.item_id == recommended.item_id:
            status = "bis"
            note = "Already best in slot."
            deltas = {}
        else:
            status = "upgrade"
            note = ""
            changed += 1
            delta_rows.append(deltas)

        if pet_focus:
            note = (note + " " if note else "") + "Required pet focus."

        rows.append(
            SlotComparison(
                gear_slot=slot,
                status=status,
                current_name=current.name if current else None,
                current_id=current.item_id if current else None,
                recommended_name=recommended.name if recommended else None,
                recommended_id=recommended.item_id if recommended else None,
                recommended_tier=recommended.tier if recommended else "",
                recommended_icon_id=recommended.icon_id if recommended else None,
                current_icon_id=current_icon,
                deltas=deltas,
                note=note.strip(),
                pet_focus=pet_focus,
                scored=True,
            )
        )

    return CharacterRaidBis(
        character=character.character,
        server=character.server,
        class_abbr=class_abbr,
        display_name=character.display_name,
        persona_key=character.persona_key,
        slots=rows,
        total_deltas=sum_deltas(delta_rows),
        slots_changed=changed,
    )


def resolve_equipped_stats(
    characters: list[CharacterGear],
    catalog: list[RaidGearCandidate],
    *,
    item_html_by_id: dict[int, str] | None = None,
    allow_network: bool = True,
) -> dict[int, RaidGearCandidate]:
    known = {c.item_id for c in catalog if c.item_id > 0}
    needed: list[int] = []
    for ch in characters:
        for item in ch.slots.values():
            if item.item_id > 0 and item.item_id not in known:
                needed.append(item.item_id)
    if not needed:
        return {}
    return hydrate_item_ids(
        needed,
        item_html_by_id=item_html_by_id,
        allow_network=allow_network,
    )
