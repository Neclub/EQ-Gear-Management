# Development — EQ Gear Management (EQGM)

Engineering guide for running from source, the CLI, local caches, and catalog internals. End-user `.exe` instructions stay in [HowToUse.md](HowToUse.md) and the [wiki](wiki/Home.md). Expansion launch work is in [Expansion Update Plan](Expansion%20Update%20Plan/README.md).

---

## Layout

| Path | Role |
|------|------|
| `src/inventory_parser/` | Package (`cli`, `web_gui`, parsers, exporters) |
| `src/inventory_parser/data/` | Bundled JSON/HTML (spell catalog, cheat sheet, GUI, report template, `heroic_aas.json`) |
| `src/inventory_parser/data/gui/` | Setup-screen HTML/JS/CSS (pywebview) |
| `src/inventory_parser/slot2_augs/` | Type 7/8 recommendations + shared EQ Resource helpers |
| `src/inventory_parser/type5_augs/` | Type 5 display (reuses Type 7/8 socket maps; Vanquisher labels) |
| `src/inventory_parser/type18_augs/` | Type 18/19 catalog + Zarax suggestions |
| `src/inventory_parser/raid_bis/` | Current-expansion raid T1/T2 compare |
| `src/inventory_parser/heroic_aas.py` | Hero's Special AAs catalog match against achievement dumps |
| `scripts/` | PyInstaller, signing, vendor/spell/Heroic AA scrapes |
| `tests/` | pytest; HTML fixtures under `tests/fixtures/` |
| `wiki/` | GitHub wiki source (user guide) |
| `.github/workflows/build-release.yml` | Windows exe + GitHub Release on `main` |

---

## Setup

Requires **Python 3.10+**. The Windows GUI needs **WebView2** (Edge runtime).

```powershell
py -3 -m pip install -e ".[dev]"
py -3 -m pytest
```

| Command | What it runs |
|---------|----------------|
| `py -3 -m inventory_parser.web_gui` | HTML GUI (`run_gui.bat` does an editable install, then this) |
| `py -3 -m inventory_parser` | CLI (`eqgm` / `inventory-parser` after install) |
| `py -3 -m pytest` | Offline unit tests (see [Tests](#tests)) |

Do not point the GUI or CLI at live `%LOCALAPPDATA%\EQGM\` during tests. `tests/conftest.py` redirects `settings_path()` to a temp file and stubs chest-class / gear-tier network lookups; other modules still read that folder if you call them with `allow_network=True`.

---

## Architecture

```
*-Inventory.txt (+ optional MissingSpells / Achievements)
        │
        ▼
  parser / team_report / missing_spells / achievement_parser
        │
        ▼
  export_bundle.build_export_bundle()   ← shared Excel + HTML payload
        │
        ├── slot2_augs / type5_augs / type18_augs / raid_bis  (optional tabs)
        ├── spell_report / useful_spells / rune_inventory
        └── achievement_report (collections, quests, raids, Heroic AA, summary)
        ▼
  excel_export  +  html_export (team_report.html)
```

**GUI:** `web_gui` hosts `data/gui/` in pywebview (982×765, dark-fantasy chrome) and calls `web_api.WebApi` (folder pickers, roster, tier colors, generate on a background thread). Default browser opens the HTML report; the setup window stays open.

**CLI:** `cli.generate_workbook()` → same `build_export_bundle()`, then writes `.xlsx` and optionally HTML.

**Constraint:** `build_export_bundle()` defaults `include_type5`, `include_type18`, and `include_raid_bis` to **False**. The GUI chips and CLI flags default those tabs **on**. Callers that import the Python API must pass the flags explicitly.

---

## CLI

Console scripts: `eqgm`, `inventory-parser` (same `cli:main`). Output path is required.

```powershell
eqgm --folder "C:\EverQuest" -o "%USERPROFILE%\Downloads\Bristlebane_Team Inventory.xlsx" --also-html
eqgm CharN_bristle-Inventory.txt -o report.xlsx --no-slot2 --no-type18 --no-raid-bis
eqgm --version
```

EQ writes `/outputfile` dumps to the **EverQuest install root**, not `Logs`.

| Flag | Default | Notes |
|------|---------|--------|
| `inventories…` | — | Explicit `*-Inventory.txt` (and optional spell/achievement files) |
| `--folder` | — | Non-recursive: `*-Inventory.txt` in that folder, plus `*-MissingSpells.txt` and `*-Achievements.txt`. Also picks `AchievementData\`. Does **not** add `SpellData\` to the path list (see below) |
| `-o` / `--output` | required | `.xlsx` path |
| `--slots` | `all` | `all` / `visible` / `non_visible`. The GUI dropped this control in 1.32.0 and always exports all slots |
| `--no-spells` / `--no-achievements` | off | Skip those tabs even if files exist |
| `--slot2` / `--no-slot2` | on | Type 7/8 |
| `--type5` / `--no-type5` | on | Type 5 display |
| `--type18` / `--no-type18` | on | Type 18/19 |
| `--raid-bis` / `--no-raid-bis` | on | Raid BiS |
| `--include-anniversary` | off | Type 7/8 Gem of Distant Echoes |
| `--also-html` | off | Write `{stem}.html` next to the workbook |

`--folder` does **not** recurse into persona subfolders (`PAL\CharN_…`). Pass those files explicitly, or use the GUI EQ Folder picker on a flat EverQuest directory (class-tagged names in the same folder are the supported persona layout).

**SpellData difference:** the GUI folder picker always scans a sibling `SpellData\` directory. CLI `--folder` only globs MissingSpells in the folder itself. If that glob finds any files, they become an explicit spell list and a sibling `SpellData\` is **not** also scanned. If the folder has **no** root MissingSpells files, later pairing still auto-discovers `SpellData\` next to each inventory. Put spell files either all next to inventories or all in `SpellData\` (GUI scans both).

There is no `--force-refresh`. Stale EQ Resource data is fixed by deleting cache files (below).

---

## Local data and cache refresh

Settings and network caches share one directory (`slot2_augs.paths.appdata_dir()`):

| Platform | Directory |
|----------|-----------|
| Windows | `%LOCALAPPDATA%\EQGM\` |
| Other | `~/.local/share/EQGM/` |

If `settings.json` is missing, Windows still copies a legacy `%LOCALAPPDATA%\Inventory Parser\settings.json` when present.

### `settings.json`

| Key | Purpose |
|-----|---------|
| `character_column_order` | Persona keys for Excel/HTML column order |
| `output_format` | `excel` / `html` / `both` |
| `last_eq_folder` | Last EverQuest install root (must still exist) |
| `tier_colors` | Five-bucket hex map (`green` / `yellow` / `orange` / `red` / `evolver`). Omitted after **Reset to default** |

### Cache files

Later generates skip live EQ Resource searches when these files already have rows (Type 7/8 and Raid BiS catalogs since 1.34.10; Type 18/19 since 1.34.2). GUI and CLI do **not** expose `force_refresh` — delete the relevant JSON (EQGM can stay closed) and regenerate.

| File | Used by |
|------|---------|
| `eqresource_search_cache.json` | Type 7/8 catalog search |
| `eqresource_aug_cache.json` | Type 7/8 / Type 5 item pages (`stats_v` must be ≥ 4) |
| `eqresource_expansion_cache.json` | Expansion labels for augs |
| `eqresource_gear_tier_cache.json` | Unknown gear T-codes — **including failed lookups** (`ok: false`), so `???` items are not re-fetched every run |
| `item_sockets_cache.json` | Type 7/8 and Type 5 holes |
| `item_class_cache.json` | Worn-chest class |
| `raidloot_cache.json` | Type 7/8 raidloot fallback |
| `eqresource_type18_catalog_cache.json` | Type 18/19 search rows |
| `eqresource_type18_item_meta_cache.json` | Type 18/19 item pages (slot types, lore, Spell Damage; `stats_v` ≥ 2) |
| `raid_bis_catalog.json` / `raid_bis_item_cache.json` | Raid BiS (`_version` must match `ITEM_CACHE_VERSION` in `raid_bis/catalog.py`) |
| `item_icons/` | Raid BiS HTML icons |
| `weight_overrides.json` | Optional persistent Type 7/8 weight overrides |

Keep `settings.json` if you only want a catalog refresh. Deleting the whole folder also drops roster order, last EQ Folder, output-format preference, and custom tier colors.

Remaining live item lookups (gear T-level, Type 18/19 item meta, Raid BiS jewelry pages) run with a small thread pool (typically 6 workers).

---

## Type 18/19 internals

Feature is still marked work-in-progress in the UI. Flow:

1. **Catalog** (`type18_augs/catalog.py`) — Type 18 saved search `searchid=255223`; Type 19 advanced search with `augtype=19` (not `augslot`). Dual `18, 19` classifies as Type 18; `19` only as Type 19.
2. **Hydrate** — item pages supply slot types, lore group, Item Lore, Mana / Spell Damage.
3. **Suggest** (`suggestions.py`) — packaged `data/type18_cheat_sheet.json` (Zarax). Defense-family names move Primary → Optional. Top two unused **Fortification** augs append to Optional; unused **Enhancement** augs go under **Filler**. Ranking is HP, then AC, then heroic sum (`stats_rank_key`).
4. **Owned / equipped** — inventory IDs and names; equipped holes from `parser.collect_equipped_aug_locations()` (equipment `*-SlotN` only; paired slots as `Ear-1`, `Fingers-1`, `Wrist-1`). HTML shows a location chip next to **Owned**; an **Alternative** that is owned and equipped gets Owned + slot, otherwise the craft anvil.

**EQ Resource constraints (do not “fix” by adding `page=2` on Type 19 POST):**

- Member search caps at **50 rows** and ignores POST `page` (page 2 repeats page 1).
- Catalog fetch always merges focused name queries (`Jubilation`, `Enduring Harmony`, `Selenelion`, Devotee/Silver category splits, …) with **6** parallel workers.
- Setting both `augslot` and `augtype` to 19 returns **zero** rows.
- Back cloaks `Mantle/Cloak/Cape of Enduring Harmony` are dropped; they are not Type 18/19 augs.
- Anniversary markers are **Jubilation** and **Enduring Harmony** only. Selenelion is a jeweler craft, not anniversary.

When `eqresource_type18_catalog_cache.json` already has `rows`, live Type 19 searches are skipped (dozens of POSTs). Delete that file **and** `eqresource_type18_item_meta_cache.json` after EQ Resource catalog changes, or Spell Damage / slot types can stay stale.

---

## Type 5 Vanquisher labels

`type5_augs/vanquisher.py` is a hardcoded catalog (item id first, then casefolded name): Master's Curio, Divine Medallion, Mythic Charm, Defiant Claw, Arcane Tome → short labels `Vanq ToL` / `Vanq NoS` / `Vanq LS` / `Vanq ToB` / `Vanq SoR` linked to the expansion Vanquisher achievement. Add a new expansion reward here when the next Vanquisher Type 5 exists; there is no scrape.

---

## Heroic AA

`achievement_report` matches each `/outputfile achievements` dump against bundled `data/heroic_aas.json` (Fanra Hero's Special AAs). Matching uses `heroic_aas.normalize_heroic_name()` (straight quotes, `saviour` → `savior`, `:Name` spacing).

Each catalog row stores whether that achievement **awards** Fortitude / Resolution / Vitality (0 or 1). HTML omits F/R/V chips when the rank is 0; Excel leaves those cells blank. Lit vs muted follows Completed / Incomplete, not the 0/1 award flags.

| Script | Purpose |
|--------|---------|
| `scripts/convert_heroic_aas.py` | Rebuild `heroic_aas.json` from a Fanra-export spreadsheet (script default path `Examples/Achievements/Heroic AA.xlsx` is not in the repo) |
| `scripts/enrich_heroic_aa_eqresource_ids.py` | Fill `eqresource_id` from achievements.eqresource.com subcategory pages |

Add new expansion bases to `EXPANSION_BASES` in the enrich script when EQ Resource publishes them.

---

## Class weights (Type 7/8 and Raid BiS)

Packaged under `data/weights/`:

- `roles.json` — tank AC+HDex, priest HWis, INT caster Spell Damage, melee/hybrid HDex
- `classes.json` — class → role/profile, plus **DRU** modifiers (`spell_damage` 9, `hwis` −9) so Druid scores Spell Damage first and HWis 1
- `slot_overlays.json` — per-slot tweaks

GUI **Advanced weights** (single-character roster) is a per-generate session override, not `weight_overrides.json`.

---

## Tests

```powershell
py -3 -m pytest
py -3 -m pytest tests/test_type18_augs.py tests/test_heroic_aas.py tests/test_type5_augs.py
```

`tests/conftest.py` autouse fixtures:

- Redirect `settings_path()` to a temp file (except `test_settings_path_uses_eqgm_appdata`)
- Block live chest-class and EQ Resource T-code fetches unless the test passes HTML overrides

Type 18/19 and Raid BiS tests use `tests/fixtures/eqresource_*.html` the same way — do not add tests that hit the network.

---

## Release

1. Set `__version__` in `src/inventory_parser/__init__.py`.
2. Add a dated section at the top of [CHANGELOG.md](CHANGELOG.md) (keep `## [Unreleased]`).
3. Merge to `main`. [build-release.yml](.github/workflows/build-release.yml) runs on Windows, builds `dist/EQGM-<version>.exe` via `scripts/run_pyinstaller.py`, publishes GitHub Release `v<version>`, and posts Discord if `DISCORD_WEBHOOK_URL` is set.

Local Windows exe: `build_exe.bat` (editable install + PyInstaller + optional Authenticode). Copy `codesign.local.bat.example` → `codesign.local.bat` (gitignored) for signing. GitHub Actions does **not** sign. Version info on the exe uses company **Lubworks**.

Installed copies check `api.github.com/repos/Neclub/EQ-Gear-Management/releases/latest` (`app_updates.py`). Download URLs must be this repo’s HTTPS `EQGM-x.y.z.exe` release asset; the app opens the browser and never runs the file.

---

## Pitfalls

- **Stale Type 18/19 after an EQ Resource change** — cache hits skip the Type 19 search. Delete the two `eqresource_type18_*.json` files.
- **Stale Type 7/8 or Raid BiS catalogs** — same pattern since 1.34.10; delete `eqresource_search_cache.json` and/or `raid_bis_catalog.json` + `raid_bis_item_cache.json`.
- **Gear T-Level stuck on `???`** — failed lookups are stored (`ok: false`). Delete `eqresource_gear_tier_cache.json` after EQ Resource gains the item.
- **Type 19 catalog empty in a scratch fetch** — `augslot=19` together with `augtype=19` is wrong; Fits Aug Slot is `augtype` only.
- **Python API missing Type 5 / 18 / Raid BiS tabs** — `build_export_bundle()` leaves those off unless you pass `include_*=True`.
- **CLI `--folder` misses persona subfolders and may miss `SpellData\`** — discovery is non-recursive; class-tagged files must sit in the folder you pass. See SpellData difference above.
- **GUI blank on Windows** — install the WebView2 Evergreen runtime.
- **HowToUse.md and `wiki/` are exe-only** — CLI and build steps were removed from the user guide in 1.30.2 on purpose; keep them here.
