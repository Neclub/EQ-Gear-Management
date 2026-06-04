"""One-off helper to refresh R1 vendor item JSON from EQ Resource pages."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "inventory_parser" / "data"

PAGES = {
    "sor_r1_vendor_items.json": ("https://sor.eqresource.com/raidvendorgood.php", "SOR-R1", "sor"),
    "tob_r1_vendor_items.json": ("https://tob.eqresource.com/raidvendor.php", "TOB-R1", "tob"),
    "ls_r1_vendor_items.json": ("https://ls.eqresource.com/raidvendor.php", "LS-R1", "ls"),
    "nos_r1_vendor_items.json": ("https://nos.eqresource.com/raidvendor.php", "NoS-R1", "nos"),
    "ani27_raid_items.json": (
        "https://items.eqresource.com/itemsearch.php?raidevent=Tides%20of%20Time:%20Glaze%20of%20the%20Ice%20Dragon",
        "ANI27",
        "ani",
    ),
}

TRADESKILL_SUFFIXES = (
    " Lining",
    " Polishing Cloth",
    " Fastener",
    " Clasp",
    " Buckle",
    " Enarmes",
    " String Serving",
    " Core of",
    " Essence of",
)

LINK_RE = re.compile(
    r'<a\s+href=(?:"|\')?(?:https?://items\.eqresource\.com/)?items\.php\?id=(?P<id>\d+)(?:"|\')?>(?P<name>[^<]+)</a>',
    re.I,
)


def should_skip(name: str, expansion: str) -> bool:
    if expansion == "sor" and name.startswith("Fractured"):
        return any(suffix in name for suffix in TRADESKILL_SUFFIXES)
    if expansion == "tob" and " of Rebellion" in name:
        return True
    if expansion == "tob" and name.startswith("Energized ") and " Engram" in name:
        return True
    if expansion == "tob" and name == "Reinforced Scalewrought Footlocker":
        return True
    if expansion == "ls" and name.startswith("Valiant"):
        return True
    if expansion == "ls" and name == "Laurion Inn Hope Chest":
        return True
    if expansion == "nos" and name.startswith("Apparitional"):
        return True
    if expansion == "nos" and " Symbol of Shar Vahl" in name:
        return True
    if expansion == "nos" and name == "Shik'Nar Carapace Crate":
        return True
    return False


def extract_items(html: str) -> list[tuple[str, int]]:
    return [(match.group("name").strip(), int(match.group("id"))) for match in LINK_RE.finditer(html)]


def main() -> None:
    for filename, (url, tier, exp) in PAGES.items():
        html = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
        items = []
        seen: set[str] = set()
        for name, item_id in extract_items(html):
            if name in seen or should_skip(name, exp):
                continue
            seen.add(name)
            items.append({"name": name, "tier_code": tier, "item_id": item_id})
        items.sort(key=lambda row: row["name"].lower())
        path = DATA_DIR / filename
        path.write_text(json.dumps({"tier_code": tier, "items": items}, indent=2) + "\n", encoding="utf-8")
        print(f"{filename}: {len(items)} items")


if __name__ == "__main__":
    main()
