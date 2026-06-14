# Changelog

All notable changes to Inventory Parser are documented here. Version numbers follow [Semantic Versioning](https://semver.org/).

**To release a new version:** edit `__version__` in `src/inventory_parser/__init__.py`, then add an entry below.

## [Unreleased]

## [1.14.0] - 2026-06-14

### Added

- **GitHub Releases automation:** every push to `main` builds `InventoryParser-x.y.z.exe` on Windows and publishes it to [GitHub Releases](https://github.com/Neclub/Inventory-Parser/releases).

### Changed

- **README** simplified for download and quick start; full usage remains in [HowToUse.md](HowToUse.md).
- **HTML report:** **Expansion** filters on achievement tabs default to the **current expansion** (newest configured) instead of **All**, so large raid lists load a smaller view first.
- **GUI polish:** refined panel layout and pill-button rendering.

## [1.13.0] - 2026-06-12

### Added

- **Rune Inventory tab** (Excel + HTML): tier × character matrix of raid rune items on hand (NoS Symbol, LS Emblem, ToB Energized Engram, SoR Mirrorshard) from General, Bank, and Shared Bank. Blank cells when count is zero; tab omitted when the team has no matching runes. No MissingSpells file required.
- **HTML Rune Inventory expansion filter:** **Expansion** dropdown (NoS, LS, ToB, SoR) on the Rune Inventory toolbar.

### Fixed

- **HTML search focus:** typing in the search box no longer blurs the input on each keystroke (only table content refreshes; toolbar controls stay mounted).

### Changed

- **Spell List renamed to Missing Spells** in Excel sheet tab, HTML sidebar, and docs (internal section id `spell_list` unchanged).
- **Gear T-Level colors:** tier code cells use semantic buckets — green (`SOR-R2`), yellow (`SOR-R1`, `ANI27`), orange (all `TOB-*`), red (everything else), purple (`Evolver` unchanged). **Team Gear** now uses the same bucket colors (replacing per gear-set hues).
- **HTML Missing Spells filters:** **Level range** (`121-125`, `126-130`) and **Rune type** (Minor → Glowing) dropdowns on the Missing Spells toolbar.
- **HTML sidebar icons:** Lucide-style stroke icons (including a dedicated Rune Inventory stack icon); active nav uses a darker blue highlight.

## [1.12.0] - 2026-06-13

### Changed

- **HTML report redesign (sidebar navigator):** dark-themed browser report with a left **sidebar** (EQ logo, section icons, navigation), main content area (server title, search, filters), and footer **gear-tier legend** on Team Gear. Still a single self-contained `.html` file — no web server required.
- **HTML navigation & filters:**
  - **Character filter** chips directly under the section list (filters gear columns and table rows)
  - **Visible slots** dropdown on gear tabs (replaces the old Visibility column)
  - **Character** and **Expansion** dropdowns on table tabs (Spell List, Raid Achievements, Missing Collections, etc.)
  - Sticky, compact **Slot** column; item names link to EQ Resource
- **HTML export metadata:** report title (`{Server} Team Inventory`), character count, and embedded EQ icon.
- Renamed Excel/HTML section label **Team gear** → **Team Gear** in the HTML export.

### Added

- Backup snapshot before HTML redesign: [`backup/pre-html-redesign/`](backup/pre-html-redesign/) (restore via [`RESTORE.md`](backup/pre-html-redesign/RESTORE.md)).

## [1.11.0] - 2026-06-13

### Changed

- **GUI redesign (calm unified layout):** unified blue accent, subtle panel cards, **Team characters** list with side action buttons (Add files / Add folder, Remove, Up, Down, Clear), horizontal **Spells** / **Achievements** / **HTML** chip toggles, layered dark backgrounds (window, cards, recessed list/path fields), EQ app icon, dark Windows title bar, and **Help** link in the header.
- **Generate Report** — primary action button renamed from **Generate Excel** (still writes the `.xlsx` workbook; HTML too when enabled).
- **HTML export** is **on by default** in the GUI (**HTML** chip); uncheck to skip the browser report.
- Shared GUI palette in [`gui_theme.py`](src/inventory_parser/gui_theme.py).

## [1.10.0] - 2026-06-12

### Changed

- **Crew → Team rename:** user-facing labels, default export filenames (`Team Inventory.xlsx`), Excel/HTML tab **Team gear**, GUI **Team characters (column order)**, and internal module names (`team_report.py`, `TeamGearReport`, etc.). Legacy `Crew Inventory` output paths are still recognized for auto-default save locations.
- **GUI buttons** use anti-aliased **pill-shaped** controls (color-coded: blue primary actions, teal secondary, red destructive, green **Generate Excel**).
- **Slots** checkboxes use teal hover text instead of bright white on mouseover.
- **Dependencies:** [Pillow](https://pypi.org/project/Pillow/) (`>=10.0`) for smooth button rendering in the GUI (installed automatically with `pip install -e .` and bundled in the `.exe` build).
- **Export memory:** parsed report data and large HTML/Excel intermediates are released after each generate; pill-button images are cleaned up on redraw.

### Fixed

- **PyInstaller build:** Pillow is no longer excluded from the frozen executable (`scripts/run_pyinstaller.py`).

## [1.9.1] - 2026-05-26

### Added

- **Character column order:** the main file list is now a **Crew characters (column order)** roster showing toon names (e.g. `Deflub ( PAL )`) instead of log file paths.
  - **Move up** / **Move down** choose which character appears in the first Excel/HTML column — useful when you always want your tank (or main) first.
  - Order is saved automatically to `%LOCALAPPDATA%\Inventory Parser\settings.json` (Windows) and restored the next time you run the app.
  - New characters are appended at the bottom until you reorder them.

### Changed

- **Remove selected** and **Clear all** operate on characters in the roster; associated inventory, MissingSpells, and achievement files for that character are removed from the export.
- Column order applies to **Crew Gear**, **Gear T-Level**, spell tabs, **Unmade Gear**, and the interactive HTML report when enabled.

## [1.9.0] - 2026-05-26

### Added

- **Interactive HTML report (optional):** checkbox **Also generate HTML report** in the GUI and CLI flag **`--also-html`** write a self-contained `{prefix}_Crew Inventory.html` next to the Excel file.
  - Same data as the workbook: Crew gear, Gear T-Level, spells, Unmade Gear, and achievement tabs when enabled.
  - Tab navigation, search, sortable columns, character/expansion filters, gear-set colors, and EQ Resource item links.
  - Opens locally in any browser — no web server required.

### Changed

- Export assembly refactored into [`export_bundle.py`](src/inventory_parser/export_bundle.py) shared by Excel and HTML writers.
- [HowToUse.md](HowToUse.md) and [Discord_Instructions.txt](Discord_Instructions.txt) document the HTML export option.

### Fixed

- HTML report search and filter controls keep keyboard focus while typing (only table content refreshes, not the control bar).

## [1.8.0] - 2026-05-25

### Added

- **Achievements export (Phase 1):** optional achievement tabs when `*-Achievements.txt` dumps from `/outputfile achievements` are included.
  - **Missing Collections** — incomplete collection items under **Collections** sections; **Char Has** shows which crew member has the item in inventory.
  - **Raid Achievements** — incomplete raid objectives only (no duplicate parent raid rows).
  - **Achievement Summary** — top-level achievement completion counts per section (expansion or category).
  - Achievement files can sit next to inventory dumps or in an **`AchievementData/`** subfolder (same pattern as `SpellData/`).
  - GUI checkbox **Include achievements** and CLI flag **`--no-achievements`**.
  - Expansion columns use release-year labels (e.g. `Shattering of Ro (2025)`) and sort **newest to oldest**.

### Fixed

- **Add folder…** **Add selected** now only adds characters visible for the current server filter (hidden rows are no longer included).

### Changed

- [HowToUse.md](HowToUse.md) and [Discord_Instructions.txt](Discord_Instructions.txt) document `/outputfile achievements` and the new tabs.

## [1.7.5] - 2026-05-25

### Added

- **Unmade Gear** Excel tab: scans **General** bags for SoR/ToB craft mats and T1 containers, listing only items where the character still needs that tier upgrade in the target slot.
  - SoR T2: **Fractured** tradeskill mats (target `SOR-R2`)
  - ToB T2: **of Rebellion** tradeskill mats (target `TOB-R2`)
  - SoR T1: **Diminished Shattered** armor containers (target `SOR-R1`)
  - ToB T1: **Obscured … Armor of the Bound** containers (target `TOB-R1`)
  - Excludes literal **Ore** items and finished gear in bags (e.g. `Defender's Charm of Rebellion`, `Legionnaire Helm of the Bound`).
  - Tab is omitted when no matching rows are found.
- Optional **Authenticode code signing** after `build_exe.bat` completes (`scripts/sign_exe.py`, `codesign.local.bat.example`). Copy to `codesign.local.bat` and set `IP_SIGN_PFX` or `IP_SIGN_THUMBPRINT` to sign release builds; skipped when not configured.

### Changed

- [HowToUse.md](HowToUse.md) and [Discord_Instructions.txt](Discord_Instructions.txt) document the **Unmade Gear** tab and optional code signing setup.

## [1.7.4] - 2026-05-25

### Added

- **Add folder…** now opens a character picker with checkboxes instead of loading every file at once. Select which characters to include before adding them to the export list.
- Server filter dropdown in the picker (e.g. **All servers**, **Bristlebane (bristle)**, **Xegony (xegony)**) to narrow a large mixed folder down to one server at a time.
- **Select all** / **Select none** apply to the characters visible for the current server filter.

### Changed

- MissingSpells files in a **`SpellData/`** subfolder are grouped with the matching character when scanning a folder for the picker.
- Picker dialog layout and styling: fixed footer with **Add selected** and **Cancel** always visible, scrollable character list, and improved combobox/scrollbar colors for dark mode.

## [1.7.3] - 2026-05-25

### Changed

- Missing Rk. II spells at rune-relevant levels (121–130) are now counted in Missing Runes / Spell List the same as missing Rk. III; duplicate entries are suppressed when both ranks appear for the same spell at the same level.
- Spell List / rune reports always show **Rk. III** in the spell name, even when the dump lists the character as missing **Rk. II** (since missing Rk. II implies they also lack the Rk. III rune turn-in).
- Arie hates his alts so much he doesn't put Rk II spells on them.

## [1.7.2] - 2026-05-24

### Fixed

- Explicitly selected MissingSpells files now produce a Crew Gear / Gear T-Level column labeled with that class (e.g. `Deflub ( PAL )` or `Deflub ( WAR )`), even when other spell files for the same character exist in the folder. Only the files you add to the export are used for persona pairing when any MissingSpells files are selected.

### Changed

- Auto-discovered spell files (inventory only, no MissingSpells in the file list) still omit Crew Gear when multiple classes share one inventory dump.

## [1.7.1] - 2026-05-24

### Fixed

- Crew Gear and Gear T-Level no longer show columns for personas that share one inventory dump with other spell files; equipped gear reflects only the active persona at dump time. Spell tabs still include every selected MissingSpells class. Use subfolders with separate inventory dumps per persona for multi-class gear tracking.

## [1.7.0] - 2026-05-24

### Changed

- **Spell-driven persona pairing:** inventory files always use `CharacterName_server-Inventory.txt` (no class suffix); MissingSpells filenames are the sole source of class/persona identity
- Multiple MissingSpells files for one character in the same folder now produce multiple persona columns sharing one inventory dump (no rename required)
- Subfolder layout supported: standard inventory filename co-located with each persona’s spell file (e.g. `PAL/Deflub_bristle-Inventory.txt` + `PAL/Deflub_bristle-PAL-MissingSpells.txt`)

## [1.6.0] - 2026-05-24

### Added

- **Alternate persona support:** multiple inventory dumps per character when filenames include an optional class suffix (e.g. `Deflub_bristle-PAL-Inventory.txt`), paired with matching `*-CLASS-MissingSpells.txt` files; Excel columns show `Deflub ( PAL )` and `Deflub ( SHD )` side by side
- Warning when multiple MissingSpells files exist for one character but the inventory file lacks a class suffix (rename inventory using the class from the spell log)

## [1.5.0] - 2026-05-21

### Added

- Character class abbreviation in Excel column headers and spell sheets (e.g. `Deflub ( PAL )`), resolved from matching `*-CLASS-MissingSpells.txt` files in the inventory folder or `SpellData` subfolder

## [1.4.0] - 2026-05-21

### Changed

- Default export filename uses the character name when only one inventory dump is selected (e.g. `Deflub_Crew Inventory.xlsx`); multi-character exports still use the server display name (e.g. `Bristlebane_Crew Inventory.xlsx`)

### Fixed

- Equipped Resonant Fracture (SoR-R2) gear is no longer misclassified as Evolver when the final augment slot appears in the inventory dump; tier codes and Fracture coloring now take precedence over Evolver detection

## [1.3.0] - 2026-05-21

### Changed

- Default export filename includes server display name from input log filenames (inventory, MissingSpells, and `eqlog_*` in the same folder), mapped via official EQ server slugs (e.g. `Bristlebane_Crew Inventory.xlsx`)

## [1.2.0] - 2026-05-20

### Changed

- Renamed Excel sheet **SOR gaps** to **Gear T-Level**
- Gear T-Level sheet now shows `SOR-R2` for equipped Resonant Fracture (current SoR raid) gear; blank cells mean empty slots only

## [1.1.0] - 2026-05-19

### Added

- SOR gaps sheet uses expansion tier codes (e.g. `TOB-R2`, `LS-G1`) instead of legacy markers
- Vendor/raid equipment lists for SOR, TOB, LS, NoS R1 non-visible gear and ANI27 (Enduring Harmony)
- `Evolver` label on SOR gaps for Evolver slots
- `???` label for unrecognized equipped gear

### Changed

- Secondary weapons are no longer classified as Evolvers

## [1.0.0] - 2026-05-19

### Added

- Version numbering in GUI title, About dialog, CLI `--version`, and Windows `.exe` properties
- Crew gear, SOR gaps, Missing Runes, and Spell List Excel export
- GUI and CLI; optional missing-spells support from `/outputfile missingspells`
