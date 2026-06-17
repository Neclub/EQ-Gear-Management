"""Scrape EQ Resource spell search pages for level 121-130 Rk. III expansion data."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from inventory_parser.spell_scrape import (
    EXPANSION_BY_IMAGE,
    LEVEL_MAX,
    LEVEL_MIN,
    catalog_key,
    parse_spell_search_html,
)

ROOT = Path(__file__).resolve().parents[1]
CLASS_URLS_FILE = ROOT / "Examples" / "SpellData" / "Class120_130.txt"
OUTPUT_FILE = ROOT / "src" / "inventory_parser" / "data" / "spell_expansions_121_130.json"
CACHE_DIR = ROOT / "Examples" / "SpellData" / "scrape_cache"

USER_AGENT = "InventoryParser/1.0 (spell catalog scraper; local dev tool)"
REQUEST_DELAY_SEC = 1.0

CLASS_URL_RE = re.compile(
    r"https://spells\.eqresource\.com/spellsearch\.php\?.*class=(?P<class>[a-z]+)",
    re.I,
)


def load_class_urls(path: Path) -> list[tuple[str, str]]:
    """Return (CLASS_ABBR, url) pairs from Class120_130.txt."""
    pairs: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        _label, url = line.split(":", 1)
        url = url.strip()
        match = CLASS_URL_RE.search(url)
        if not match:
            raise ValueError(f"Could not parse class from URL line: {line!r}")
        class_abbr = match.group("class").upper()
        pairs.append((class_abbr, url))
    return pairs


def fetch_html(url: str, *, cache_path: Path | None = None) -> str:
    if cache_path is not None and cache_path.is_file():
        return cache_path.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to fetch {url}: {exc}") from exc
    text = data.decode("utf-8", errors="replace")
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
    return text


def build_catalog(
    class_urls: list[tuple[str, str]],
    *,
    use_cache: bool = False,
    delay_sec: float = REQUEST_DELAY_SEC,
) -> dict[str, object]:
    catalog: dict[str, dict[str, dict[str, object]]] = {}
    counts_by_class: dict[str, int] = {}

    for index, (class_abbr, url) in enumerate(class_urls):
        cache_path = CACHE_DIR / f"{class_abbr.lower()}.html" if use_cache else None
        if index > 0 and not (use_cache and cache_path and cache_path.is_file()):
            time.sleep(delay_sec)
        html = fetch_html(url, cache_path=cache_path if use_cache else None)
        parsed = parse_spell_search_html(html)
        class_spells: dict[str, dict[str, object]] = {}
        for spell in parsed:
            key = catalog_key(int(spell["level"]), str(spell["name"]))
            class_spells[key] = {
                "level": spell["level"],
                "name": spell["name"],
                "expansion": spell["expansion"],
                "spell_id": spell["spell_id"],
            }
        catalog[class_abbr] = class_spells
        counts_by_class[class_abbr] = len(class_spells)
        print(f"{class_abbr}: {len(class_spells)} Rk. III spells")

    if any(count == 0 for count in counts_by_class.values()):
        empty = [k for k, v in counts_by_class.items() if v == 0]
        raise SystemExit(f"No spells scraped for class(es): {', '.join(empty)}")

    return {
        "version": 1,
        "source": "https://spells.eqresource.com/spellsearch.php",
        "level_min": LEVEL_MIN,
        "level_max": LEVEL_MAX,
        "spells": catalog,
    }


def validate_catalog(data: dict[str, object]) -> None:
    spells = data.get("spells")
    if not isinstance(spells, dict):
        raise SystemExit("Catalog missing spells object")
    for class_abbr, class_spells in spells.items():
        if not isinstance(class_spells, dict):
            raise SystemExit(f"Invalid spells entry for {class_abbr}")
        for key, entry in class_spells.items():
            if not isinstance(entry, dict):
                raise SystemExit(f"Invalid spell entry {class_abbr}/{key}")
            level = int(entry["level"])
            if level < LEVEL_MIN or level > LEVEL_MAX:
                raise SystemExit(f"Out-of-range level {level} for {entry.get('name')}")
            expansion = str(entry["expansion"])
            if expansion not in EXPANSION_BY_IMAGE.values():
                raise SystemExit(f"Unknown expansion {expansion!r} for {entry.get('name')}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help=f"Output JSON path (default: {OUTPUT_FILE})",
    )
    parser.add_argument(
        "--cache",
        action="store_true",
        help=f"Read/write HTML under {CACHE_DIR}",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY_SEC,
        help="Seconds between HTTP requests",
    )
    args = parser.parse_args()

    class_urls = load_class_urls(CLASS_URLS_FILE)
    catalog = build_catalog(class_urls, use_cache=args.cache, delay_sec=args.delay)
    validate_catalog(catalog)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(len(v) for v in catalog["spells"].values())  # type: ignore[arg-type]
    print(f"Wrote {total} spells to {args.output}")


if __name__ == "__main__":
    main()
