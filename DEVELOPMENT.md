# Development — EQ Gear Management (EQGM)

Engineering guide for running from source, the CLI, local caches, and the Type 18/19 catalog. End-user `.exe` instructions stay in [HowToUse.md](HowToUse.md). Expansion launch work is in [Expansion Update Plan](Expansion%20Update%20Plan/README.md).

---

## Layout

| Path | Role |
|------|------|
| `src/inventory_parser/` | Package (`cli`, `web_gui`, parsers, exporters) |
| `src/inventory_parser/data/` | Bundled JSON/HTML (spell catalog, cheat sheet, GUI, report template) |
| `src/inventory_parser/slot2_augs/` | Type 7/8 recommendations + shared EQ Resource helpers |
| `src/inventory_parser/type5_augs/` | Type 5 display (reuses Type 7/8 socket maps) |
| `src/inventory_parser/type18_augs/` | Type 18/19 catalog + Zarax suggestions |
| `src/inventory_parser/raid_bis/` | Current-expansion raid T1/T2 compare |
| `scripts/` | PyInstaller, signing, vendor/spell scrapes |
| `tests/` | pytest; HTML fixtures under `tests/fixtures/` |
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

Do not point the GUI or CLI at live `%LOCALAPPDATA%\EQGM\` during tests — pytest stubs chest-class and gear-tier network lookups, but other modules still read that folder if you call them with `allow_network=True`.

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
        ▼
  excel_export  +  html_export (team_report.html)
```

**GUI:** `web_gui` hosts `data/gui/` in pywebview and calls `web_api.WebApi` (folder pickers, roster order, generate on a background thread).

**CLI:** `cli.generate_workbook()` → same `build_export_bundle()`, then writes `.xlsx` and optionally HTML.

**Constraint:** `build_export_bundle()` defaults `include_type5`, `include_type18`, and `include_raid_bis` to **False**. The GUI chips and CLI flags default those tabs **on**. Callers that import the Python API must pass the flags explicitly.

---

## CLI

Console scripts: `eqgm`, `inventory-parser` (same `cli:main`). Output path is required.

```powershell
eqgm --folder "C:\EverQuest\Logs" -o "%USERPROFILE%\Downloads\Bristlebane_Team Inventory.xlsx" --also-html
eqgm CharN_bristle-Inventory.txt -o report.xlsx --no-slot2 --no-type18 --no-raid-bis
eqgm --version
```

| Flag | Default | Notes |
|------|---------|--------|
| `inventories…` | — | Explicit `*-Inventory.txt` (and optional spell/achievement files) |
| `--folder` | — | Non-recursive: `*-Inventory.txt` in that folder, plus `*-MissingSpells.txt` and `*-Achievements.txt`. Also picks `AchievementData\`. Spell pairing still looks in a sibling `SpellData\` next to each inventory |
| `-o` / `--output` | required | `.xlsx` path |
| `--slots` | `all` | `all` / `visible` / `non_visible`. The GUI dropped this control in 1.32.0 and always exports all slots |
| `--no-spells` / `--no-achievements` | off | Skip those tabs even if files exist |
| `--slot2` / `--no-slot2` | on | Type 7/8 |
| `--type5` / `--no-type5` | on | Type 5 display |
| `--type18` / `--no-type18` | on | Type 18/19 |
| `--raid-bis` / `--no-raid-bis` | on | Raid BiS |
| `--include-anniversary` | off | Type 7/8 Gem of Distant Echoes |
| `--also-html` | off | Write `{stem}.html` next to the workbook |

`--folder` does **not** recurse into persona subfolders (`PAL\CharN_…`). Pass those files explicitly, or use the GUI EQ Folder picker on a flat Logs directory (class-tagged names in the same folder are the supported persona layout). If any `*-MissingSpells.txt` files sit in the folder root, those are treated as the explicit spell list and a sibling `SpellData\` directory is not also scanned. Put spell files either all next to inventories or all in `SpellData\` (GUI folder pick scans both).

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
| `last_eq_folder` | Last Logs folder (must still exist) |

### Cache files

Later generates skip live EQ Resource searches when these files already have rows. GUI and CLI do **not** expose `force_refresh` — delete the relevant JSON (EQGM can stay closed) and regenerate.

| File | Used by |
|------|---------|
| `eqresource_search_cache.json` | Type 7/8 catalog search |
| `eqresource_aug_cache.json` | Type 7/8 / Type 5 item pages |
| `eqresource_expansion_cache.json` | Expansion labels for augs |
| `eqresource_gear_tier_cache.json` | Unknown gear T-codes |
| `item_sockets_cache.json` | Type 7/8 and Type 5 holes |
| `item_class_cache.json` | Worn-chest class |
| `raidloot_cache.json` | Type 7/8 raidloot fallback |
| `eqresource_type18_catalog_cache.json` | Type 18/19 search rows (1.34.2+) |
| `eqresource_type18_item_meta_cache.json` | Type 18/19 item pages (slot types, lore, Spell Damage) |
| `raid_bis_catalog.json` / `raid_bis_item_cache.json` | Raid BiS |
| `item_icons/` | Raid BiS HTML icons |
| `weight_overrides.json` | Optional persistent Type 7/8 weight overrides |

Keep `settings.json` if you only want a catalog refresh. Deleting the whole folder also drops roster order, last EQ Folder, and output-format preference.

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

## Tests

```powershell
py -3 -m pytest
py -3 -m pytest tests/test_type18_augs.py
```

`tests/conftest.py` autouse fixtures block live chest-class and EQ Resource T-code fetches unless the test passes HTML overrides. Type 18/19 and Raid BiS tests use `tests/fixtures/eqresource_*.html` the same way — do not add tests that hit the network.

---

## Release

1. Set `__version__` in `src/inventory_parser/__init__.py`.
2. Add a dated section at the top of [CHANGELOG.md](CHANGELOG.md) (keep `## [Unreleased]`).
3. Merge to `main`. [build-release.yml](.github/workflows/build-release.yml) runs on Windows, builds `dist/EQGM-<version>.exe` via `scripts/run_pyinstaller.py`, publishes GitHub Release `v<version>`, and posts Discord if `DISCORD_WEBHOOK_URL` is set.

Local Windows exe: `build_exe.bat` (editable install + PyInstaller + optional Authenticode). Copy `codesign.local.bat.example` → `codesign.local.bat` (gitignored) for signing. GitHub Actions does **not** sign.

Installed copies check `api.github.com/repos/Neclub/EQ-Gear-Management/releases/latest` (`app_updates.py`). Download URLs must be this repo’s HTTPS `EQGM-x.y.z.exe` release asset; the app opens the browser and never runs the file.

---

## Pitfalls

- **Stale Type 18/19 after an EQ Resource change** — cache hits skip the Type 19 search. Delete the two `eqresource_type18_*.json` files.
- **Type 19 catalog empty in a scratch fetch** — `augslot=19` together with `augtype=19` is wrong; Fits Aug Slot is `augtype` only.
- **Python API missing Type 5 / 18 / Raid BiS tabs** — `build_export_bundle()` leaves those off unless you pass `include_*=True`.
- **CLI `--folder` misses persona subfolders** — discovery is non-recursive; class-tagged files must sit in the folder you pass.
- **GUI blank on Windows** — install the WebView2 Evergreen runtime.
- **HowToUse.md is exe-only** — CLI and build steps were removed in 1.30.2 on purpose; keep them here, not in the user guide.
