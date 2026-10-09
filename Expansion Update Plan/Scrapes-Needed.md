# Scrapes Needed for the Next Expansion

Target: **December 2026** EQ expansion — **Favors of Fortune** (official; EQ Resource 33rd expansion). Codes: **FoF** / **fof** / **FOF**. EQ Gear Management does not scrape at runtime — these are **dev-only** refreshes that produce bundled JSON under [`src/inventory_parser/data/`](../src/inventory_parser/data/).

Full phased procedure (gear regex, runes, achievements, tests): [`December-2026-Expansion-Update.md`](December-2026-Expansion-Update.md).

**Status (2026-10-09):** Logged-in [fof.eqresource.com](https://fof.eqresource.com/) has a live home page and armor matrices. **Raid Vendor `raidvendor.php` is 404.** `raidvendorgood.php` is not in the FoF menu. Spell expansion icon on spells.eqresource.com is not confirmed (item pages already use `expacimages/fof.jpg`). **Do not change production code or run scrapes during beta prep.** Run scrapes **1–3** only when those pages list finished items.

Existing vendor pages were re-scraped successfully (SoR 64, ToB 63, LS 60, NoS 63, ANI27 14). Added SoR skip for `Mirrorshard of Relic` spell runes that appeared on the raid vendor page. New `fof_r1_vendor_items.json` **PAGES** entry and `should_skip()` rules remain blocked until `raidvendor.php` lists real items (section 1.2). Armor matrices are the beta keyword source, not this scrape.

Spell catalog re-scraped from cache (1016 Rk. III spells across 16 classes) using current `EXPANSION_BY_IMAGE` (`ls.jpg` / `tob.jpg` / `sor.jpg`). FoF spell-image mapping remains blocked until a spell row shows the icon filename (section 1.4; expected `fof.jpg`).

---

## Actual scrapes (run these)

### 1. FoF R1 raid vendor page

| | |
|--|--|
| **Script** | [`scripts/build_vendor_json.py`](../scripts/build_vendor_json.py) |
| **Source** | Menu URL `https://fof.eqresource.com/raidvendor.php` (404 as of 2026-10-09). `raidvendorgood.php` is not in the FoF menu — re-check before scraping in case Good/Evil pages appear |
| **Output** | `fof_r1_vendor_items.json` |
| **Why** | Exact-name → `FOF-R1` for vendor gear that subtitle regex does not catch |

**Prep before scrape:** add a `PAGES` entry and `should_skip()` rules (tradeskill mats, runes, containers) from December plan 1.2 / 1.5 / 1.6.

**Template `PAGES` entry:**
```python
"fof_r1_vendor_items.json": (
    "https://fof.eqresource.com/raidvendor.php",  # or raidvendorgood.php
    "FOF-R1",
    "fof",
),
```

**Command:**
```powershell
py -3 scripts/build_vendor_json.py
```

Re-scrapes all existing vendor pages too: SoR, ToB, LS, NoS, ANI27.

**Phase 1 record:**
- R1 vendor URL: `https://fof.eqresource.com/raidvendor.php` (404; content not confirmed)
- Tier code: `FOF-R1`
- Skip rules: `TBD`

---

### 2. Anniversary / special raid event (if applicable)

| | |
|--|--|
| **Script** | Same `build_vendor_json.py` |
| **Source** | `https://items.eqresource.com/itemsearch.php?raidevent=...` |
| **Output** | e.g. `ani##_raid_items.json` |
| **Why** | Distinct anniversary gear set (like current ANI27 Ice Dragon) |

Mark **N/A** if the December patch has no separate raid-event gear set. See December plan **1.3**.

**Phase 1 record:**
- Raid event search URL: `TBD` (or N/A)
- Name keyword / tier code: `TBD`

---

### 3. Spell expansion catalog (all 16 classes)

| | |
|--|--|
| **Script** | [`scripts/scrape_spell_expansions.py`](../scripts/scrape_spell_expansions.py) |
| **URLs** | 16 class spellsearch links in [`Examples/SpellData/Class120_130.txt`](../Examples/SpellData/Class120_130.txt) |
| **Output** | [`spell_expansions_121_130.json`](../src/inventory_parser/data/spell_expansions_121_130.json) |
| **Why** | Tags Missing Spells / Missing Runes with the correct expansion |

**Prep before scrape:**
- Map FoF icon in [`spell_scrape.py`](../src/inventory_parser/spell_scrape.py) `EXPANSION_BY_IMAGE` (confirm filename in December plan **1.4**; expected `fof.jpg` → `Favors of Fortune`)
- If spells go above 130: bump `LEVEL_MAX` and update class URLs

**Template `EXPANSION_BY_IMAGE` entry:**
```python
"fof.jpg": "Favors of Fortune",  # confirm filename in 1.4
```

**Command:**
```powershell
py -3 scripts/scrape_spell_expansions.py --cache
```

That is **16 HTTP fetches** (one per class), unless cache hits.

**Phase 1 record:**
- Image filename: `TBD.jpg` (expected `fof.jpg`)
- Canonical expansion name: `Favors of Fortune`
- `LEVEL_MAX`: `130` (confirm; bump if 131+)
- Spell level block for FoF: `TBD–TBD`

---

## Not a web scrape (still refresh if source updates)

### 4. Useful-spells list (Raccoo xlsx → JSON)

December plan **1.14**.

| | |
|--|--|
| **Script** | [`scripts/convert_useful_spells.py`](../scripts/convert_useful_spells.py) |
| **Input** | Manually download updated xlsx into `Examples/SpellData/` |
| **Output** | [`useful_spells.json`](../src/inventory_parser/data/useful_spells.json) |
| **Source sheet** | [Raccoo useful spells](https://docs.google.com/spreadsheets/d/1ZqUFZ-WTZvfcBfwu5g6GGEQroEwNLSfK1LMOdMHVHcA/htmlview) |

**Command:**
```powershell
py -3 scripts/convert_useful_spells.py
```

**Status:** Skip until Raccoo publishes a list for Favors of Fortune. Current file remains `SOR - Raccoo's list of useful spells.xlsx`. Convert re-run 2026-07-27 against that xlsx (612 spells / 16 classes; no catalog change).

---

## Scrape count summary

| # | What | Pages / fetches | Script | Ready? |
|---|------|-----------------|--------|--------|
| 1 | FoF R1 raid vendor | 1 new page (+ re-fetch of 4–5 existing) | `build_vendor_json.py` | Blocked — `raidvendor.php` is 404 |
| 2 | Anniversary raid (optional) | 0 or 1 | `build_vendor_json.py` | Blocked — TBD / N/A |
| 3 | Spell catalog by class | **16** | `scrape_spell_expansions.py` | Blocked — image map TBD |
| 4 | Useful spells | 0 (manual xlsx + convert) | `convert_useful_spells.py` | Skip — no FoF xlsx |

**Minimum for launch day:** scrapes **1** and **3**. Add **2** if there is an anniversary set; add **4** when Raccoo’s list is updated.

---

## Not scrapes (gather by hand — needed but separate)

These are **in-game / EQ Resource inspection**, not scraper runs. See Phase 1 in the December plan:

- **1.1** Identity — Favors of Fortune / FoF / fof / FOF (official; site map in the December plan)
- **1.5** Spell rune turn-in names + level band → rune JSON / [`spell_runes.py`](../src/inventory_parser/spell_runes.py)
- **1.6** Gear tier subtitle keywords — beta candidates recorded; do not edit [`gear_tiers.py`](../src/inventory_parser/gear_tiers.py) yet
- **1.6** Tradeskill exclusion patterns — still TBD
- **1.7** Unmade bag mats / containers → [`unmade_gear.py`](../src/inventory_parser/unmade_gear.py)
- **1.8** Achievement section header → [`achievement_parser.py`](../src/inventory_parser/achievement_parser.py)
- **1.9–1.13** Colors, Vanquisher, EXPAC maps (`fof` observed, code unchanged), Heroic AA (base `3400`), Raid BiS source

---

## When to run

| When | Action |
|------|--------|
| **Now (beta prep)** | Site map and armor phrases are in the December plan. Do not scrape. Do not edit production code |
| **EQ Resource vendor page lists finished items** | Fill 1.2 / 1.4; then scrapes **1–3** (add PAGES / EXPANSION_BY_IMAGE first) |
| **+1–3 days** | Patch skip rules / regex from real bags (re-scrape only if vendor pages change) |
| **When Raccoo updates** | Convert **4** |

---

## Launch-day command sequence

After Phase 1 values are filled and code prep is done:

```powershell
py -3 scripts/build_vendor_json.py
py -3 scripts/scrape_spell_expansions.py --cache
# only if xlsx updated:
py -3 scripts/convert_useful_spells.py
```

Then continue with Phase 3–4 in [`December-2026-Expansion-Update.md`](December-2026-Expansion-Update.md).
