# Scrapes Needed for the Next Expansion

Target: **December 2026** EQ expansion (name TBD as of July 2026). EQ Gear Management does not scrape at runtime — these are **dev-only** refreshes that produce bundled JSON under [`src/inventory_parser/data/`](../src/inventory_parser/data/).

Full phased procedure (gear regex, runes, achievements, tests): [`December-2026-Expansion-Update.md`](December-2026-Expansion-Update.md).

**Status (2026-07-27):** Expansion name not announced. July Producer’s Letter teases demiplanes / fate / “Mad”. EQ Resource vendor and spell pages for the new expansion are not live yet. Run scrapes **1–3** on launch day (or when those pages appear).

Existing vendor pages were re-scraped successfully (SoR 64, ToB 63, LS 60, NoS 63, ANI27 14). Added SoR skip for `Mirrorshard of Relic` spell runes that appeared on the raid vendor page. New `{abbrev}_r1_vendor_items.json` **PAGES** entry and expansion-specific skip rules remain blocked until the R1 vendor URL is known.

Spell catalog re-scraped from cache (1016 Rk. III spells across 16 classes) using current `EXPANSION_BY_IMAGE` (`ls.jpg` / `tob.jpg` / `sor.jpg`). New expansion image mapping remains blocked until the EQ Resource icon filename is known.

---

## Actual scrapes (run these)

### 1. New expansion R1 raid vendor page

| | |
|--|--|
| **Script** | [`scripts/build_vendor_json.py`](../scripts/build_vendor_json.py) |
| **Source** | `https://[SUBDOMAIN].eqresource.com/raidvendor*.php` (exact path TBD when EQ Resource goes live) |
| **Output** | `{abbrev}_r1_vendor_items.json` |
| **Why** | Exact-name → `[ABBREV]-R1` for vendor gear that subtitle regex does not catch |

**Prep before scrape:** add a `PAGES` entry and `should_skip()` rules (tradeskill mats, runes, containers).

**Template `PAGES` entry:**
```python
"{abbrev}_r1_vendor_items.json": (
    "https://{subdomain}.eqresource.com/raidvendor.php",  # or raidvendorgood.php
    "{ABBREV}-R1",
    "{abbrev}",
),
```

**Command:**
```powershell
py -3 scripts/build_vendor_json.py
```

Re-scrapes all existing vendor pages too: SoR, ToB, LS, NoS, ANI27.

**Phase 1 record:**
- R1 vendor URL: `TBD`
- Tier code: `TBD-R1`
- Skip rules: `TBD`

---

### 2. Anniversary / special raid event (if applicable)

| | |
|--|--|
| **Script** | Same `build_vendor_json.py` |
| **Source** | `https://items.eqresource.com/itemsearch.php?raidevent=...` |
| **Output** | e.g. `ani##_raid_items.json` |
| **Why** | Distinct anniversary gear set (like current ANI27 Ice Dragon) |

Mark **N/A** if the December patch has no separate raid-event gear set.

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
- Map new expansion icon in [`spell_scrape.py`](../src/inventory_parser/spell_scrape.py) `EXPANSION_BY_IMAGE` (e.g. `{abbrev}.jpg` → full name)
- If spells go above 130: bump `LEVEL_MAX` and update class URLs

**Template `EXPANSION_BY_IMAGE` entry:**
```python
"{abbrev}.jpg": "[Expansion Full Name]",
```

**Command:**
```powershell
py -3 scripts/scrape_spell_expansions.py --cache
```

That is **16 HTTP fetches** (one per class), unless cache hits.

**Phase 1 record:**
- Image filename: `TBD.jpg`
- Canonical expansion name: `TBD`
- `LEVEL_MAX`: `130` (confirm; bump if 131+)
- Spell level block for new expansion: `TBD–TBD`

---

## Not a web scrape (still refresh if source updates)

### 4. Useful-spells list (Raccoo xlsx → JSON)

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

**Status:** Skip until Raccoo publishes a list for the new expansion. Current file remains `SOR - Raccoo's list of useful spells.xlsx`. Convert re-run 2026-07-27 against that xlsx (612 spells / 16 classes; no catalog change).

---

## Scrape count summary

| # | What | Pages / fetches | Script | Ready? |
|---|------|-----------------|--------|--------|
| 1 | New R1 raid vendor | 1 new page (+ re-fetch of 4–5 existing) | `build_vendor_json.py` | Blocked — URL TBD |
| 2 | Anniversary raid (optional) | 0 or 1 | `build_vendor_json.py` | Blocked — TBD / N/A |
| 3 | Spell catalog by class | **16** | `scrape_spell_expansions.py` | Blocked — image map TBD |
| 4 | Useful spells | 0 (manual xlsx + convert) | `convert_useful_spells.py` | Skip — no new xlsx |

**Minimum for launch day:** scrapes **1** and **3**. Add **2** if there is an anniversary set; add **4** when Raccoo’s list is updated.

---

## Not scrapes (gather by hand — needed but separate)

These are **in-game / EQ Resource inspection**, not scraper runs. See Phase 1.5–1.8 in the December plan:

- Expansion identity (name, abbrev, year, subdomain)
- Gear tier subtitle keywords (R1/R2/G1–G3) → [`gear_tiers.py`](../src/inventory_parser/gear_tiers.py)
- Tradeskill exclusion patterns
- Unmade bag mats / containers → [`unmade_gear.py`](../src/inventory_parser/unmade_gear.py)
- Spell rune turn-in names + level band → rune JSON / [`spell_runes.py`](../src/inventory_parser/spell_runes.py)
- Achievement section header string → [`achievement_parser.py`](../src/inventory_parser/achievement_parser.py)

---

## When to run

| When | Action |
|------|--------|
| **Expansion announcement** | Fill Phase 1 URLs and identity in this doc + December plan |
| **Launch day (EQ Resource live)** | Scrapes **1–3** (add PAGES / EXPANSION_BY_IMAGE first) |
| **+1–3 days** | Patch skip rules / regex from real bags (re-scrape only if vendor pages change) |
| **When Raccoo updates** | Scrape/convert **4** |

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
