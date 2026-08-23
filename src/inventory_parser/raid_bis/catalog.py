"""Fetch and parse current-expansion raid armor/jewelry from EQ Resource."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from inventory_parser.raid_bis.models import (
    ARMOR_SLOT_HEADERS,
    JEWELRY_TYPE_SLOTS,
    RaidBisCatalog,
    RaidGearCandidate,
    RaidVendorCatalog,
)
from inventory_parser.raid_bis.vendor import (
    parse_raidvendor_html,
    vendor_catalog_from_dict,
    vendor_catalog_to_dict,
)
from inventory_parser.slot2_augs.aug_stats import clean_stats, merge_stats
from inventory_parser.slot2_augs.chest_class import parse_eqresource_item_classes
from inventory_parser.slot2_augs.eqresource_augs import (
    EQRESOURCE_ITEM_URL,
    USER_AGENT,
    _NAME_RE,
    _SLOT_RE,
    _allowed_from_eqr_slot_text,
    _stats_from_eqr_html,
    parse_eqresource_lore_group,
)
from inventory_parser.slot2_augs.paths import appdata_dir

CACHE_FILENAME = "raid_bis_catalog.json"
ITEM_CACHE_FILENAME = "raid_bis_item_cache.json"
ITEM_CACHE_VERSION = 6
RAIDARMOR_URL = "https://sor.eqresource.com/raidarmor.php"
RAIDGEAR_URL = "https://sor.eqresource.com/raidgear.php"
RAIDVENDOR_URL = "https://sor.eqresource.com/raidvendorgood.php"
RAIDLOOT_SEARCH_URL = "https://www.raidloot.com/items"

_ITEM_HREF_RE = re.compile(r"items\.php\?id=(\d+)", re.IGNORECASE)
_ICON_RE = re.compile(r"itemimages/(\d+)\.(?:png|gif|jpg|webp)", re.IGNORECASE)
_FOCUS_RE = re.compile(
    r"Focus:\s*(?:<[^>]+>\s*)*([^<\n]+)",
    re.IGNORECASE,
)
_EFFECT_RE = re.compile(
    r"Effect:\s*(?:<[^>]+>\s*)*([^<\n]+)",
    re.IGNORECASE,
)
_TIER_HEAD_RE = re.compile(
    r'<a\s+name="tier(\d+)"></a>.*?<font[^>]*>\s*Tier\s+\d+\s+-\s*([^<]+)',
    re.IGNORECASE | re.DOTALL,
)
_SKIP_NAME_RE = re.compile(
    r"diminished|riven arcana|emblem of|crate of|armor lining|fractured armor",
    re.IGNORECASE,
)
_HEADER_TO_STAT = {
    "ac": "ac",
    "hp": "hp",
    "mana": "mana",
    "end": "endurance",
    "hstr": "hstr",
    "hsta": "hsta",
    "hint": "hint",
    "hwis": "hwis",
    "hagi": "hagi",
    "hdex": "hdex",
    "hcha": "hcha",
    "spell dmg": "spell_damage",
    "spell damage": "spell_damage",
}


def cache_path() -> Path:
    return appdata_dir() / CACHE_FILENAME


def item_cache_path() -> Path:
    return appdata_dir() / ITEM_CACHE_FILENAME


def _http_get(url: str, timeout: float = 45.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _load_item_cache() -> dict:
    data = _load_json(item_cache_path())
    if int(data.get("_version") or 0) != ITEM_CACHE_VERSION:
        return {}
    return {k: v for k, v in data.items() if k != "_version"}


def _save_item_cache(cache: dict) -> None:
    payload = dict(cache)
    payload["_version"] = ITEM_CACHE_VERSION
    _save_json(item_cache_path(), payload)


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def should_skip_name(name: str) -> bool:
    return bool(_SKIP_NAME_RE.search(name or ""))


def parse_raidarmor_html(html: str) -> list[RaidGearCandidate]:
    """Parse class × slot matrices on sor.eqresource.com/raidarmor.php."""
    if not html:
        return []
    parts = re.split(r'<a\s+name="tier(\d+)"></a>', html, flags=re.IGNORECASE)
    items: list[RaidGearCandidate] = []
    seen: set[int] = set()
    # split keeps delimiters: [pre, '1', block1, '2', block2, ...]
    i = 1
    while i + 1 < len(parts):
        tier_n = parts[i].strip()
        block = parts[i + 1]
        i += 2
        tier = f"T{tier_n}" if tier_n.isdigit() else ""
        items.extend(_parse_raidarmor_block(block, tier, seen))
    if not items:
        items.extend(_parse_raidarmor_block(html, "T1", seen))
    return items


def _parse_raidarmor_block(
    html: str, tier: str, seen: set[int]
) -> list[RaidGearCandidate]:
    out: list[RaidGearCandidate] = []
    header_slots: list[str] = []
    for row_m in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL):
        row = row_m.group(1)
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.IGNORECASE | re.DOTALL)
        if not cells:
            continue
        texts = [_cell_text(c) for c in cells]
        if texts and texts[0].casefold() == "class":
            header_slots = []
            for label in texts[1:]:
                mapped = ARMOR_SLOT_HEADERS.get(label.strip().casefold())
                header_slots.append(mapped or "")
            continue
        if not header_slots or len(cells) < 2:
            continue
        class_abbr = ""
        for cell in cells[1:]:
            m = re.search(r">\s*([A-Z]{3})\s*<", cell)
            if m:
                class_abbr = m.group(1).upper()
                break
        if not class_abbr:
            continue
        for idx, cell in enumerate(cells[1:]):
            if idx >= len(header_slots) or not header_slots[idx]:
                continue
            href_m = _ITEM_HREF_RE.search(cell)
            if not href_m:
                continue
            item_id = int(href_m.group(1))
            if item_id in seen:
                continue
            seen.add(item_id)
            slot = header_slots[idx]
            out.append(
                RaidGearCandidate(
                    item_id=item_id,
                    name=f"{class_abbr} {slot}",
                    classes=frozenset({class_abbr}),
                    slots=frozenset({slot}),
                    tier=tier,
                    source="EQ Resource raidarmor",
                )
            )
    return out


def _cell_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


class _GearTableParser(HTMLParser):
    """Parse raidgear.php result tables: icon, name/id, numeric stats."""

    def __init__(self) -> None:
        super().__init__()
        self._in_td = False
        self._td_parts: list[str] = []
        self._td_href = ""
        self._td_icon = ""
        self._row: list[tuple[str, str, str]] = []
        self.header: list[str] = []
        self.rows: list[tuple[int, str, str | None, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if tag == "tr":
            self._row = []
        elif tag == "td":
            self._in_td = True
            self._td_parts = []
            self._td_href = ""
            self._td_icon = ""
        elif tag == "a" and self._in_td:
            href = ad.get("href") or ""
            if href:
                self._td_href = href
        elif tag == "img" and self._in_td:
            src = ad.get("src") or ""
            m = _ICON_RE.search(src)
            if m:
                self._td_icon = m.group(1)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_td:
            self._in_td = False
            text = re.sub(r"\s+", " ", " ".join(self._td_parts)).strip()
            self._row.append((self._td_href, text, self._td_icon))
        elif tag == "tr":
            self._finish_row()

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._td_parts.append(data)

    def _finish_row(self) -> None:
        cells = self._row
        self._row = []
        if not cells:
            return
        texts = [t for _h, t, _i in cells]
        joined = " ".join(texts).casefold()
        if "item name" in joined and "ac" in joined:
            self.header = [t.strip() for t in texts]
            return
        item_id = 0
        name = ""
        icon = None
        for href, text, icon_id in cells:
            m = _ITEM_HREF_RE.search(href) or _ITEM_HREF_RE.search(text)
            if m:
                item_id = int(m.group(1))
                name = text.strip() or name
            if icon_id and not icon:
                icon = icon_id
        if item_id <= 0:
            return
        self.rows.append((item_id, name, icon, texts))


def parse_raidgear_html(
    html: str, *, default_slot: str = "", default_tier: str = ""
) -> list[RaidGearCandidate]:
    """Parse jewelry/other-slot tables from raidgear.php."""
    if not html:
        return []
    slot = default_slot or _slot_from_caption(html)
    tier = default_tier or _tier_from_caption(html)
    parser = _GearTableParser()
    try:
        parser.feed(html)
    except Exception:
        return []
    header_keys: list[str | None] = []
    for label in parser.header:
        header_keys.append(_HEADER_TO_STAT.get(label.strip().casefold()))

    out: list[RaidGearCandidate] = []
    seen: set[int] = set()
    for item_id, name, icon, texts in parser.rows:
        if item_id in seen or should_skip_name(name):
            continue
        seen.add(item_id)
        stats: dict[str, int] = {}
        if header_keys and len(texts) == len(header_keys):
            for key, raw in zip(header_keys, texts):
                if not key:
                    continue
                n = _cell_int(raw)
                if n is not None:
                    stats[key] = n
        slots = frozenset({slot}) if slot else frozenset()
        out.append(
            RaidGearCandidate(
                item_id=item_id,
                name=name or f"Item {item_id}",
                stats=clean_stats(stats),
                slots=slots,
                tier=tier,
                icon_id=icon,
                source="EQ Resource raidgear",
            )
        )
    return out


def _slot_from_caption(html: str) -> str:
    m = re.search(
        r"Search results for\s*<b><font[^>]*>([^<]+)</font></b>",
        html,
        re.IGNORECASE,
    )
    if not m:
        return ""
    label = m.group(1).strip().casefold()
    mapping = {
        "back": "Back",
        "charm": "Charm",
        "ear": "Ear",
        "face": "Face",
        "finger": "Fingers",
        "fingers": "Fingers",
        "neck": "Neck",
        "range": "Range",
        "shoulder": "Shoulders",
        "shoulders": "Shoulders",
        "waist": "Waist",
    }
    return mapping.get(label, "")


def _tier_from_caption(html: str) -> str:
    m = re.search(r"Raid Tier\s+(\d+)", html, re.IGNORECASE)
    if m:
        return f"T{m.group(1)}"
    if re.search(r"Raid Tier</font></b>\s*All", html, re.IGNORECASE):
        return ""
    return ""


def _cell_int(raw: str) -> int | None:
    text = (raw or "").strip()
    if not text or not re.fullmatch(r"-?\d+", text):
        return None
    return int(text)


def _labeled_spell_names(html: str, pattern: re.Pattern[str]) -> str:
    """Collect every Effect:/Focus: name on the page (items often have click + worn)."""
    names: list[str] = []
    seen: set[str] = set()
    for match in pattern.finditer(html or ""):
        raw = re.sub(r"\s+", " ", match.group(1)).strip()
        # Drop trailing UI suffixes like "- Casting Time: 0.5s" / "- Worn" for cleaner storage,
        # but keep the spell name itself for matching.
        name = re.split(r"\s*-\s*(?:Casting Time|Worn)\b", raw, maxsplit=1, flags=re.I)[0]
        name = name.strip(" -")
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        names.append(name)
    return "; ".join(names)


def parse_item_page(html: str, item_id: int, *, name_hint: str = "") -> RaidGearCandidate | None:
    """Hydrate stats, class, slot, focus, effect, and icon from an EQ Resource item page."""
    if not html or item_id <= 0:
        return None
    name_m = _NAME_RE.search(html)
    name = (name_m.group(1).strip() if name_m else "") or (name_hint or f"Item {item_id}")
    if should_skip_name(name):
        return None
    stats = _stats_from_eqr_html(html)
    classes = frozenset(parse_eqresource_item_classes(html))
    slot_m = _SLOT_RE.search(html)
    slot_text = slot_m.group(1).strip() if slot_m else ""
    slots = _allowed_from_eqr_slot_text(re.sub(r"\s+", " ", slot_text))
    focus = _labeled_spell_names(html, _FOCUS_RE)
    effect = _labeled_spell_names(html, _EFFECT_RE)
    icon_m = _ICON_RE.search(html)
    tier = ""
    if re.search(r"Raid\s*[-–]\s*Tier\s*2", html, re.IGNORECASE):
        tier = "T2"
    elif re.search(r"Raid\s*[-–]\s*Tier\s*1", html, re.IGNORECASE):
        tier = "T1"
    return RaidGearCandidate(
        item_id=item_id,
        name=name,
        stats=clean_stats(stats),
        classes=classes,
        slots=slots,
        tier=tier,
        lore_group=parse_eqresource_lore_group(html),
        icon_id=icon_m.group(1) if icon_m else None,
        focus=focus,
        effect=effect,
        source="EQ Resource",
    )


def _better_name(base: RaidGearCandidate, extra: RaidGearCandidate) -> str:
    extra_name = (extra.name or "").strip()
    base_name = (base.name or "").strip()
    if re.fullmatch(r"[A-Z]{3} \w+", base_name) and extra_name and extra_name != base_name:
        return extra_name
    return extra_name or base_name


def merge_hydrated(base: RaidGearCandidate, extra: RaidGearCandidate) -> RaidGearCandidate:
    # Prefer the longer effect/focus string (hydrated pages list click + worn).
    focus = extra.focus if len(extra.focus or "") >= len(base.focus or "") else base.focus
    effect = extra.effect if len(extra.effect or "") >= len(base.effect or "") else base.effect
    return RaidGearCandidate(
        item_id=base.item_id,
        name=_better_name(base, extra),
        stats=merge_stats(base.stats, extra.stats),
        classes=extra.classes or base.classes,
        slots=extra.slots or base.slots,
        tier=extra.tier or base.tier,
        lore_group=extra.lore_group or base.lore_group,
        icon_id=extra.icon_id or base.icon_id,
        focus=focus or "",
        effect=effect or "",
        source=extra.source or base.source,
    )


def raidgear_url(slot_type: str, *, tier: str = "4") -> str:
    q = urllib.parse.urlencode(
        {"class": "", "type": slot_type, "stat": "ac", "tier": tier, "Submit": "Submit"}
    )
    return f"{RAIDGEAR_URL}?{q}"


def _candidate_to_dict(item: RaidGearCandidate) -> dict:
    return {
        "item_id": item.item_id,
        "name": item.name,
        "stats": dict(item.stats),
        "classes": sorted(item.classes),
        "slots": sorted(item.slots),
        "tier": item.tier,
        "lore_group": item.lore_group,
        "icon_id": item.icon_id,
        "focus": item.focus,
        "effect": item.effect,
        "source": item.source,
    }


def _candidate_from_dict(raw: dict) -> RaidGearCandidate:
    return RaidGearCandidate(
        item_id=int(raw["item_id"]),
        name=str(raw.get("name") or f"Item {raw['item_id']}"),
        stats=clean_stats(raw.get("stats") or {}),
        classes=frozenset(str(c).upper() for c in (raw.get("classes") or [])),
        slots=frozenset(str(s) for s in (raw.get("slots") or [])),
        tier=str(raw.get("tier") or ""),
        lore_group=raw.get("lore_group"),
        icon_id=raw.get("icon_id"),
        focus=str(raw.get("focus") or ""),
        effect=str(raw.get("effect") or ""),
        source=str(raw.get("source") or "EQ Resource"),
    )


def fetch_catalog(
    *,
    force_refresh: bool = False,
    allow_network: bool = True,
    html_overrides: dict[str, str] | None = None,
    item_html_by_id: dict[int, str] | None = None,
    polite_delay_s: float = 0.05,
    hydrate: bool = True,
) -> RaidBisCatalog:
    """Build the current-expansion raid armor + jewelry catalog."""
    now = datetime.now(timezone.utc).isoformat()
    html_overrides = html_overrides or {}
    item_html_by_id = item_html_by_id or {}
    cache = _load_json(cache_path())
    warning: str | None = None
    urls: list[str] = [RAIDARMOR_URL, RAIDVENDOR_URL]
    items: list[RaidGearCandidate] = []
    from_cache = False
    vendor: RaidVendorCatalog | None = None

    try:
        armor_html = html_overrides.get("raidarmor")
        if armor_html is None:
            if not allow_network:
                raise RuntimeError("network disabled")
            armor_html = _http_get(RAIDARMOR_URL)
        items.extend(parse_raidarmor_html(armor_html))

        for slot_type, slot_name in JEWELRY_TYPE_SLOTS:
            key = f"raidgear:{slot_type}"
            url = raidgear_url(slot_type)
            urls.append(url)
            gear_html = html_overrides.get(key)
            if gear_html is None:
                if not allow_network:
                    continue
                if polite_delay_s > 0:
                    time.sleep(polite_delay_s)
                gear_html = _http_get(url)
            items.extend(
                parse_raidgear_html(gear_html, default_slot=slot_name)
            )
        if not items:
            raise ValueError("EQ Resource raid catalog returned no items")
        vendor = _load_vendor(
            html_overrides=html_overrides,
            allow_network=allow_network,
            polite_delay_s=polite_delay_s,
            cache=cache,
            now=now,
            force_refresh=force_refresh,
        )
        if html_overrides or allow_network:
            cache["catalog"] = {
                "fetched_at": now,
                "urls": urls,
                "items": [_candidate_to_dict(i) for i in items],
            }
            if vendor is not None:
                cache["vendor"] = vendor_catalog_to_dict(vendor)
                cache["vendor"]["fetched_at"] = now
            if not html_overrides:
                _save_json(cache_path(), cache)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, RuntimeError) as exc:
        cached = cache.get("catalog") if not force_refresh else None
        if cached and cached.get("items"):
            items = [_candidate_from_dict(d) for d in cached["items"]]
            from_cache = True
            warning = f"Live EQ Resource raid catalog failed ({exc}); using cache."
            vendor = vendor_catalog_from_dict(cache.get("vendor"))
        else:
            fallback = _raidloot_fallback(
                allow_network=allow_network and not html_overrides,
                html_overrides=html_overrides,
            )
            if fallback:
                items = fallback
                warning = f"EQ Resource raid catalog failed ({exc}); using raidloot fallback."
                vendor = _load_vendor(
                    html_overrides=html_overrides,
                    allow_network=allow_network,
                    polite_delay_s=polite_delay_s,
                    cache=cache,
                    now=now,
                    force_refresh=force_refresh,
                )
            else:
                return RaidBisCatalog(
                    items=[],
                    fetched_at=now,
                    from_cache=False,
                    warning=f"Raid BiS catalog failed ({exc}).",
                    urls=urls,
                    vendor=_load_vendor(
                        html_overrides=html_overrides,
                        allow_network=False,
                        polite_delay_s=0,
                        cache=cache,
                        now=now,
                        force_refresh=force_refresh,
                    ),
                )

    by_id: dict[int, RaidGearCandidate] = {}
    for item in items:
        by_id.setdefault(item.item_id, item)

    if hydrate:
        hydrate_network = bool(allow_network) and not html_overrides
        hydrated = _hydrate_items(
            list(by_id.values()),
            item_html_by_id=item_html_by_id,
            allow_network=hydrate_network,
            polite_delay_s=polite_delay_s,
        )
        for item_id, extra in hydrated.items():
            base = by_id.get(item_id)
            if base is None:
                by_id[item_id] = extra
            else:
                by_id[item_id] = merge_hydrated(base, extra)

    ready = [i for i in by_id.values() if i.item_id > 0 and not should_skip_name(i.name)]
    if vendor is None:
        vendor = _load_vendor(
            html_overrides=html_overrides,
            allow_network=allow_network and not html_overrides,
            polite_delay_s=polite_delay_s,
            cache=cache,
            now=now,
            force_refresh=force_refresh,
        )
    return RaidBisCatalog(
        items=ready,
        fetched_at=now,
        from_cache=from_cache,
        warning=warning,
        urls=urls,
        vendor=vendor,
    )


def _load_vendor(
    *,
    html_overrides: dict[str, str],
    allow_network: bool,
    polite_delay_s: float,
    cache: dict,
    now: str,
    force_refresh: bool,
) -> RaidVendorCatalog | None:
    html = html_overrides.get("raidvendor")
    if html is None and allow_network:
        if polite_delay_s > 0:
            time.sleep(polite_delay_s)
        try:
            html = _http_get(RAIDVENDOR_URL)
        except (urllib.error.URLError, TimeoutError, OSError):
            html = None
    if html:
        vendor = parse_raidvendor_html(html, url=RAIDVENDOR_URL)
        vendor.fetched_at = now
        if vendor.items or vendor.currency_name:
            return vendor
    if html_overrides or force_refresh:
        return None
    return vendor_catalog_from_dict(cache.get("vendor"))


def _hydrate_items(
    items: list[RaidGearCandidate],
    *,
    item_html_by_id: dict[int, str],
    allow_network: bool,
    polite_delay_s: float,
) -> dict[int, RaidGearCandidate]:
    item_cache = _load_item_cache()
    out: dict[int, RaidGearCandidate] = {}
    fetched = 0
    for item in items:
        key = str(item.item_id)
        html = item_html_by_id.get(item.item_id)
        parsed: RaidGearCandidate | None = None
        if html is not None:
            parsed = parse_item_page(html, item.item_id, name_hint=item.name)
        elif key in item_cache and item_cache[key].get("ok"):
            parsed = _candidate_from_dict(item_cache[key]["item"])
        elif allow_network:
            if fetched and polite_delay_s > 0:
                time.sleep(polite_delay_s)
            try:
                html = _http_get(EQRESOURCE_ITEM_URL.format(item_id=item.item_id))
                parsed = parse_item_page(html, item.item_id, name_hint=item.name)
                fetched += 1
            except (urllib.error.URLError, TimeoutError, OSError, ValueError):
                parsed = None
            item_cache[key] = {
                "ok": parsed is not None,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "item": _candidate_to_dict(parsed) if parsed else None,
            }
        if parsed is not None:
            out[item.item_id] = parsed
    if fetched and allow_network:
        _save_item_cache(item_cache)
    elif item_html_by_id and not allow_network:
        pass
    elif item_html_by_id:
        _save_item_cache(item_cache)
    return out


def hydrate_item_ids(
    item_ids: list[int],
    *,
    item_html_by_id: dict[int, str] | None = None,
    allow_network: bool = True,
    polite_delay_s: float = 0.05,
) -> dict[int, RaidGearCandidate]:
    """Fetch/cache EQ Resource pages for equipped items not already in the catalog."""
    stubs = [RaidGearCandidate(item_id=i, name=f"Item {i}") for i in item_ids if i > 0]
    return _hydrate_items(
        stubs,
        item_html_by_id=item_html_by_id or {},
        allow_network=allow_network,
        polite_delay_s=polite_delay_s,
    )


def _raidloot_fallback(
    *,
    allow_network: bool,
    html_overrides: dict[str, str],
) -> list[RaidGearCandidate]:
    html = html_overrides.get("raidloot")
    if html is None:
        if not allow_network:
            return []
        try:
            q = urllib.parse.urlencode(
                {"type": "Armor", "source": "Shattering of Ro", "order": "AC"}
            )
            html = _http_get(f"{RAIDLOOT_SEARCH_URL}?{q}")
        except (urllib.error.URLError, TimeoutError, OSError):
            return []
    return parse_raidloot_armor_html(html)


def parse_raidloot_armor_html(html: str) -> list[RaidGearCandidate]:
    """Minimal raidloot item-table parser used only as a catalog fallback."""
    if not html:
        return []
    out: list[RaidGearCandidate] = []
    seen: set[int] = set()
    for m in re.finditer(
        r'href="[^"]*[?&]id=(\d+)[^"]*"[^>]*>([^<]+)',
        html,
        re.IGNORECASE,
    ):
        item_id = int(m.group(1))
        name = re.sub(r"\s+", " ", m.group(2)).strip()
        if item_id in seen or not name or should_skip_name(name):
            continue
        seen.add(item_id)
        out.append(
            RaidGearCandidate(
                item_id=item_id,
                name=name,
                source="raidloot",
            )
        )
    if out:
        return out
    for m in re.finditer(
        r"items\.php\?id=(\d+)[^<]*>([^<]+)",
        html,
        re.IGNORECASE,
    ):
        item_id = int(m.group(1))
        name = re.sub(r"\s+", " ", m.group(2)).strip()
        if item_id in seen or should_skip_name(name):
            continue
        seen.add(item_id)
        out.append(
            RaidGearCandidate(item_id=item_id, name=name, source="raidloot")
        )
    return out
