"""Fetch EQ Resource achievement IDs and merge into heroic_aas.json."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inventory_parser.heroic_aas import normalize_heroic_name  # noqa: E402

DEFAULT_JSON = ROOT / "src" / "inventory_parser" / "data" / "heroic_aas.json"
USER_AGENT = "EQGM-heroic-aa-id-lookup/1.0"
ACH_ROW_RE = re.compile(
    r'<a\s+class="ach-row"\s+href="achievements\.php\?id=(\d+)">.*?'
    r'<span\s+class="nm">([^<]+)</span>',
    re.I | re.S,
)

# Expansion category bases on achievements.eqresource.com (COTF through SoR).
EXPANSION_BASES = {
    "Call of the Forsaken": 2100,
    "The Darkened Sea": 2200,
    "The Broken Mirror": 2300,
    "Empires of Kunark": 2400,
    "Ring of Scale": 2500,
    "The Burning Lands": 2600,
    "Torment of Velious": 2700,
    "Claws of Veeshan": 2800,
    "Terror of Luclin": 2900,
    "Night of Shadows": 3000,
    "Laurion's Song": 3100,
    "The Outer Brood": 3200,
    "Shattering of Ro": 3300,
}


def _http_get(url: str, timeout: float = 45.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def subcategory_ids_for_base(base: int) -> list[int]:
    """Likely subcategory ids under an expansion category base."""
    # Common suffixes: 01 general, 02/03 exploration/progression, 04 quests,
    # 05 missions, 06/07 raids/conquests, 08 hunts, 09 collections, 10 special.
    candidates = [base + offset for offset in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)]
    # CoV uses slightly different numbering (2801, 2803-2808).
    return sorted(set(candidates))


def scrape_subcategory(sub_id: int) -> list[tuple[int, str]]:
    url = f"https://achievements.eqresource.com/subcategories.php?id={sub_id}"
    try:
        page = _http_get(url)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  skip {sub_id}: {exc}")
        return []
    return [
        (int(m.group(1)), html.unescape(m.group(2).strip()))
        for m in ACH_ROW_RE.finditer(page)
    ]


def build_name_index() -> dict[str, int]:
    index: dict[str, int] = {}
    for expansion, base in EXPANSION_BASES.items():
        print(f"Scraping {expansion} ({base})…")
        for sub_id in subcategory_ids_for_base(base):
            rows = scrape_subcategory(sub_id)
            if not rows:
                continue
            print(f"  {sub_id}: {len(rows)} achievements")
            for ach_id, name in rows:
                key = normalize_heroic_name(name)
                # Prefer first seen; duplicates should be the same id.
                index.setdefault(key, ach_id)
            time.sleep(0.15)
    return index


def normalize_cached_index(raw: dict) -> dict[str, int]:
    """Rebuild a name->id map, unescaping HTML entities from older caches."""
    index: dict[str, int] = {}
    for key, value in raw.items():
        normalized = normalize_heroic_name(html.unescape(str(key)))
        index.setdefault(normalized, int(value))
    return index


def match_id(entry: dict, index: dict[str, int]) -> int | None:
    names = [str(entry.get("name", "") or "")]
    aliases = entry.get("aliases") or []
    if isinstance(aliases, list):
        names.extend(str(a) for a in aliases if a)
    for name in names:
        key = normalize_heroic_name(name)
        if key in index:
            return index[key]
    return None


def enrich(payload: dict, index: dict[str, int]) -> tuple[int, list[str]]:
    matched = 0
    missing: list[str] = []
    for entry in payload.get("achievements") or []:
        if not isinstance(entry, dict):
            continue
        ach_id = match_id(entry, index)
        if ach_id is None:
            missing.append(str(entry.get("name", "")))
            entry.pop("eqresource_id", None)
            continue
        entry["eqresource_id"] = ach_id
        matched += 1
    return matched, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--cache",
        type=Path,
        default=ROOT / "scripts" / "_eqr_achievement_index.json",
        help="Optional cache of scraped name->id map",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-scrape EQ Resource even if cache exists",
    )
    args = parser.parse_args(argv)

    if args.cache.is_file() and not args.refresh:
        print(f"Loading cache {args.cache}")
        index = normalize_cached_index(
            json.loads(args.cache.read_text(encoding="utf-8"))
        )
    else:
        index = build_name_index()
        # Store under original scraped keys already normalized.
        args.cache.write_text(
            json.dumps(index, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote cache {args.cache} ({len(index)} names)")

    payload = json.loads(args.json.read_text(encoding="utf-8"))
    matched, missing = enrich(payload, index)
    args.json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    total = len(payload.get("achievements") or [])
    print(f"Matched {matched}/{total} achievements in {args.json}")
    if missing:
        print(f"Unmatched ({len(missing)}):")
        for name in missing:
            print(f"  - {name}")
    return 0 if matched == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
