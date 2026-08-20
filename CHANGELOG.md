# Changelog

All notable changes to EQ Gear Management (EQGM) are documented here. Version numbers follow [Semantic Versioning](https://semver.org/).

**To release a new version:** edit `__version__` in `src/inventory_parser/__init__.py`, then add an entry below.

## [Unreleased]

## [1.30.1] - 2026-08-20

### Changed

- **Missing Collections:** omit **Stalking Fear** (Rain of Fear). It still counts toward Achievement Summary totals.

## [1.30.0] - 2026-08-20

### Added

- **Type 5 Augs** tab (Excel and HTML): display-only list of equipped type 5 augs (and Empty holes) per gear slot, with expansion, heroic stats, and sortable HTML columns. No upgrade suggestions. Character filter on the HTML toolbar. Link to the current [EQ Resource Type 5 list](https://items.eqresource.com/itemsearch.php?searchid=481762). Toggle with the **Type 5 Augs** Include chip (on by default) or CLI `--type5` / `--no-type5`. Socket maps and aug/expansion lookups reuse the `%LOCALAPPDATA%\EQGM\` cache shared with Type 7/8.

## [1.29.0] - 2026-08-20

### Added

- **GUI:** checks GitHub Releases when the app opens. If a newer `EQGM-x.y.z.exe` is available, a popup shows the current and newest versions and asks whether to download. Offline or up-to-date launches stay quiet. **Help → Check for Updates** still runs the same check on demand. Download links must be this repo's HTTPS GitHub Release asset; the app opens the link in the browser and never runs the file.

## [1.28.3] - 2026-08-20

### Changed

- **Raid BiS:** stat changes and overall totals include **AC** for tank classes (WAR, PAL, SHD) and omit **Mana** for WAR, ROG, MNK, and BER.

### Fixed

- **Raid BiS:** an item already equipped is not recommended as BiS for a different slot. Wrists can still share a bracer.

## [1.28.2] - 2026-08-19

### Fixed

- **Unmade Gear:** raid craft mats and T1 containers in General bags were omitted when the matching slot was already at (or above) the material's target, or was an Evolver. Every recognized unmade item is now listed so you can see it is still in inventory. Equipped Tier remains for context. For rings, ears, and wrists, Target Slot prefers a paired slot that is still below the material's target when one exists.

## [1.28.1] - 2026-08-19

### Changed

- **HTML reports:** item names and filter labels with special characters display correctly.
- **GUI:** failed exports show a short status message.

### Docs

- Discord guide rewritten as four paste-ready messages (what EQGM is, what the report shows, in-game files, using the program).
- HowToUse, README, and Discord note that Raid BiS does not score Evolvers (they may still be BiS).

## [1.28.0] - 2026-08-19

### Changed

- **HTML sidebar:** section buttons match the Lub Inventory index cards — dark plates, gold hover ring, blue active state, and high-contrast labels.
- **HTML title:** the report title is drawn as a rounded nameplate (EQGM crest, gold underline, character count and date) in the same gold-and-dark theme.

## [1.27.0] - 2026-08-17

### Added

- **Raid BiS** tab (Excel and HTML) compares equipped armor and jewelry to current-expansion raid T1 and T2, scored with the same class/slot weights as Type 7/8 augs. T1 can beat T2. MAG/BST/NEC keep a pet-focus ear (`Enhanced Minion` or `Summoner` in the name). Weapons, Ammo, and Power Source are shown but not scored. Wrists are not Lore, so both slots can recommend the same bracer. HTML uses an in-game inventory paperdoll (green = already BiS, gold = upgrade) with a **Character** dropdown (`Name ( CLASS )`). Stat changes list HP, Mana, primary HStat, and Spell Damage for casters. Catalog is EQ Resource (raidloot fallback); icons are cached at generate time under `%LOCALAPPDATA%\EQGM\`.

### Fixed

- EQ Resource item pages that include **Purity**, or **Luck** / **Backstab** in the combat block, now parse AC, HP, Mana, and Spell Damage.

## [1.26.0] - 2026-08-17

### Added

- **Quests** tab (Excel and HTML) lists unfinished Mercenary and Partisan zone quest lines from `/outputfile achievements`. Partial lines show each child quest as **Done** or **Missing**. HTML groups each line under an achievement header with a checklist, plus Character, Expansion, and Zone filters.
- **Raid Achievements** HTML matches the Quests layout. Each unfinished raid is grouped under the **Conqueror** header; child rows are the event achievements (the text after the event name). HTML adds an **Event** filter. Excel includes **Event** and **Status** columns.
- **Missing Collections** HTML: click a missing item name to copy it; a small balloon confirms it was added to the clipboard.

## [1.25.1] - 2026-08-16

### Changed

- User-facing copy uses **output files** / **inventory files** instead of **dumps**, and drops casual wording such as **toon** in docs and the GUI.

## [1.25.0] - 2026-08-16

### Added

- **HTML Missing Runes:** **Sort** dropdown reorders character columns (roster order, name, class, most missing). **Expansion** filter matches Rune Inventory so “most missing” can target one expansion.

### Changed

- Windows `.exe` file properties now list **Lubworks** as company and copyright (`Copyright © 2026 Lubworks`).

## [1.24.1] - 2026-08-16

### Fixed

- Type 7/8 recommendations ignore augs that fit only other hole types (for example type 5 **Immovable Green Gem**). EQ Resource item pages are parsed for `fits in slot types`, and equipped non-7/8 augs are not reused as recommendations for other slots.

## [1.24.0] - 2026-08-16

### Added

- Equipped **Velium Empowered Gem of Freezing** (item 163584) is treated as a must-have type 7/8 aug. It stays in the loadout on a legal slot (Arms, Back, Charm, Chest, Ear, Face, Feet, Finger, Hands, Head, Legs, Neck, Range, Shoulder, Waist, Wrist). The hole is the one that keeps the best weighted stat trade-off versus true BiS for the rest of the set.

## [1.23.2] - 2026-08-15

### Removed

- Local `Examples/` inventory dumps are no longer in the GitHub repository (kept on disk for development only).

## [1.23.1] - 2026-08-15

### Fixed

- The setup window grows to fit **Export options** (including **Include Anniversary augs** and Advanced weights) instead of clipping those controls.

## [1.23.0] - 2026-08-15

### Added

- Equipped items with no name/vendor T-code are looked up on EQ Resource (expansion + Raid/Group tier). Known codes such as `SOR-R2` replace `???`; older or unmapped pages stay `???`.

### Changed

- Character class is taken from the **worn Chest (BP)** on each inventory dump (raidloot, then EQ Resource). MissingSpells and class-tagged inventory filenames are fallback when the chest is empty or the lookup has no class.
- **Docs:** README, HowToUse, and Discord guide note Live-only / Laurion's Song scope, class from worn Chest, and EQ Resource T-codes for unknown gear.

## [1.22.0] - 2026-08-15

### Added

- **Help → Check for Updates:** compares the running app version to the latest GitHub Release. If a newer `EQGM-x.y.z.exe` is available, asks **Would you like to download?** (Yes / No); otherwise reports **You have the latest version.**

## [1.21.0] - 2026-08-14

### Changed

- Rebranded the app to **EQ Gear Management** (**EQGM**). Settings and caches now live under `%LOCALAPPDATA%\EQGM\` (existing Inventory Parser settings are copied on first run). Release exe is `EQGM-x.y.z.exe`.
- Replaced the Windows icon, GUI header badge, and HTML report logo/favicon with the EQGM crest.
- **Docs:** README, HowToUse, Discord guide, and expansion-update notes updated for EQGM, Type 7/8 Augs, Unmade Gear, CLI flags, and current GUI labels.

### Removed

- Unused design mockups, class-icon reference sets, local backup snapshots, and generated example workbooks from the repository.

## [1.20.0] - 2026-08-14

### Added

- **Type 7/8 Augs** optional export: type 7/8 BiS recommendations, Need to farm, ranked reference, and stat summary. Toggle with the **Type 7/8 Augs** Include chip (on by default when inventories are loaded). Extra Excel sheets and an HTML section are added only when the chip is on.
- **Artisan's Prize** Ear recommendations use the inventory dump (no checkbox). **Include Anniversary augs** plus session-only Advanced weights for a single character.
- Generate progress bar while Slot2 catalogs and sockets are fetched (EQ Resource, with raidloot fallback). Caches live under `%LOCALAPPDATA%\EQGM\`.
- CLI: `--slot2` / `--no-slot2`, `--include-anniversary`.
- **Type 7/8 Augs HTML:** Character dropdown when the report includes more than one character; sidebar chips filter those rows by persona display name.
- **Type 7/8 Augs HTML:** Need to farm table columns are sortable (click Aug to group the same item). Missing Focus/ore components show **Need** plus the item name; owned components still show **Have**. The Include chip and HTML tab are labeled **Type 7/8 Augs**.
- **GUI:** Folder picker and roster grow with the window, but stay inside the Windows work area (above the taskbar). Drag the EQGM header or a dialog title to move the window.

## [1.19.0] - 2026-07-27

### Added

- **Output format selector** next to **Generate Report**: Excel, HTML, or Both. Choice is remembered between sessions.

### Changed

- Removed the Export-options **HTML** chip (format is chosen beside Generate).
- HTML-only export writes the `.html` report without creating an Excel workbook.
- **Docs:** HowToUse and Discord guide updated for the output format selector.

## [1.18.2] - 2026-07-15

### Changed

- **HTML Character filter** chips support multi-select. Unselected chips dim only while a filter is active; default (All) stays full strength.
- Persona chips use full display names when the same character has multiple classes (e.g. `Deflub ( PAL )`), so each persona can be toggled independently.
- **Docs:** HowToUse and Discord guide updated for multi-select and persona filter chips.

### Fixed

- Selecting a multi-persona character no longer collapses to the first persona only.

## [1.18.1] - 2026-07-15

### Changed

- **HTML export filename** uses underscores throughout (e.g. `Bristlebane_Team_Inventory.html`). Excel names are unchanged (`Bristlebane_Team Inventory.xlsx`).
- **Docs:** HowToUse, README, and Discord guide updated for HTML naming and shared persona achievements.

### Fixed

- **Missing Collections / Achievement Summary / Raid Achievements** are counted once per character when multiple Alternate Persona inventory dumps exist. Classes share achievements and collections; Char Has also lists each character once.

## [1.18.0] - 2026-07-15

### Added

- **Class-tagged inventory filenames** for Alternate Personas: `CharacterName_server-CLASS-Inventory.txt` (same pattern as MissingSpells). Each class dump is its own Team Gear column with that persona’s equipped gear.
- When any class-tagged inventory exists for a character, the generic `CharacterName_server-Inventory.txt` for that character is ignored.
- Class-tagged inventory without a Matching MissingSpells file still produces a labeled gear column.
- Example dumps under `Examples/SpecialNaming/`.

### Changed

- **Docs:** HowToUse, README, and Discord guide updated for class-tagged inventory naming and persona columns.

## [1.17.0] - 2026-07-10

### Added

- **Missing Useful Spells** tab (Excel + HTML): intersects each character’s MissingSpells dump with Raccoo’s curated useful-spell list (all levels), with Character / Expansion filters and a credit link to the source spreadsheet.
- Bundled `useful_spells.json` plus `scripts/convert_useful_spells.py` to refresh the list from the Raccoo xlsx (`SHK` sheet maps to `SHD`).

### Changed

- **Docs:** README, HowToUse, Discord guide, and changelog updated for the new tab.

## [1.16.3] - 2026-07-10

### Changed

- **Export performance:** each inventory dump is parsed once per report and reused for Unmade Gear, Rune Inventory, and achievement “Char Has” lookups (including shared-inventory personas).
- **Excel styling:** sheet backgrounds use end-of-sheet padding instead of painting every cell up front; tier/spell `PatternFill` colors are cached singletons.

### Fixed

- **Unmade Gear column order:** Excel now uses the same prebuilt, roster-ordered Unmade Gear rows as HTML (no second rebuild that ignored **Up** / **Down** order).

## [1.16.2] - 2026-07-07

### Changed

- **GUI HTML export:** after generation, the saved `.html` file opens in the system default browser. The setup screen stays open so **Help** and other controls remain available.
- **Docs:** README, HowToUse, and Discord guide updated for browser-based HTML opening.

### Fixed

- **Help menu** no longer stops working after report generation (setup page re-initializes reliably on load).
- **pywebview errors** when opening large in-app HTML reports (`load_html` / API callback race on Windows).

### Removed

- **In-app report viewer** from the post-export GUI flow (the HTML file is still written; the GUI opens it in your default browser instead).

## [1.16.1] - 2026-06-18

### Changed

- **Missing Runes** (Excel + HTML) now groups rune counts by spell expansion (Laurion's Song, The Outer Brood, Shattering of Ro) instead of level bands.
- **Docs:** HowToUse, README, and Discord guide updated for expansion-based runes and spells.

## [1.16.0] - 2026-06-17

### Added

- **Spell expansion catalog (121-130):** EQ Resource scraper and bundled spell data now tag Missing Spells entries with the exact expansion each Rk. III spell comes from (Laurion's Song, The Outer Brood, or Shattering of Ro).

### Changed

- **Missing Spells** (Excel + HTML) now shows **Character / Level / Rune / Expansion / Spell**; the old **Block / level band** column is removed from that detail list.
- **HTML Missing Spells filters:** removed the **Level range** dropdown; **Character**, **Rune type**, and **Expansion** remain.
- **Single-character GUI exports:** when HTML export is enabled, the `.html` file is still written, but the app no longer switches into the in-app report viewer for solo reports.

### Fixed

- **Unmade Gear target slots:** **Fractured Idol Polishing Cloth** now maps to **Range** instead of **Charm**; **Fractured Charm Polishing Cloth** still maps to **Charm**.

## [1.15.0] - 2026-06-14

### Added

- **HTML GUI (pywebview):** desktop app uses a web-based setup page and in-app report viewer that mirrors the interactive HTML export design (sidebar navigation, filters, tier colors).
- **Class icons** on roster cards — per-class SVG glyphs with color-themed badges.
- **GitHub rollback backup:** branch `backup/pre-pywebview-gui` and tag `backup/pre-pywebview-gui-2026-06-14` preserve the tkinter GUI.
- **Tests** for `web_api` helpers and team report HTML mount paths.

### Changed

- **GUI technology:** replaced tkinter + Pillow with pywebview + bundled HTML/CSS/JS. Entry point is now `inventory_parser.web_gui`.
- **Setup layout:** split pane — **Team characters** sidebar on the left; **Export options** and **Output folder** stacked on the right; roster **Up** / **Down** / **Remove** / **Clear** below Output folder; **EQ Folder** under the roster list.
- **Default window size** 860×640 for the compact setup layout.
- **pywebview file dialogs** use `FileDialog.FOLDER` / `FileDialog.SAVE` (replaces deprecated constants).
- **Dependencies:** added `pywebview`; removed `Pillow` (no longer required).

### Removed

- Tkinter GUI modules (`gui.py`, `pill_button.py`, `gui_theme.py`, `window_chrome.py`) from the active package.

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

- Backup snapshot before HTML redesign (later removed from the tree; git history still has it).

## [1.11.0] - 2026-06-13

### Changed

- **GUI redesign (calm unified layout):** unified blue accent, subtle panel cards, **Team characters** list with side action buttons (Add files / Add folder, Remove, Up, Down, Clear), horizontal **Spells** / **Achievements** / **HTML** chip toggles, layered dark backgrounds (window, cards, recessed list/path fields), EQ app icon, dark Windows title bar, and **Help** link in the header.
- **Generate Report** — primary action button renamed from **Generate Excel** (still writes the `.xlsx` workbook; HTML too when enabled).
- **HTML export** is **on by default** in the GUI (**HTML** chip); uncheck to skip the browser report.
- Shared GUI palette in `gui_theme.py` (later replaced by the HTML GUI).

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
  - Order is saved automatically to `%LOCALAPPDATA%\EQGM\settings.json` (Windows) and restored the next time you run the app.
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

- **Achievements export (Phase 1):** optional achievement tabs when `*-Achievements.txt` Output logs from `/outputfile achievements` are included.
  - **Missing Collections** — incomplete collection items under **Collections** sections; **Char Has** shows which crew member has the item in inventory.
  - **Raid Achievements** — incomplete raid objectives only (no duplicate parent raid rows).
  - **Achievement Summary** — top-level achievement completion counts per section (expansion or category).
  - Achievement files can sit next to inventory Output logs or in an **`AchievementData/`** subfolder (same pattern as `SpellData/`).
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
- Spell List / rune reports always show **Rk. III** in the spell name, even when the Output log lists the character as missing **Rk. II** (since missing Rk. II implies they also lack the Rk. III rune turn-in).
- Arie hates his alts so much he doesn't put Rk II spells on them.

## [1.7.2] - 2026-05-24

### Fixed

- Explicitly selected MissingSpells files now produce a Crew Gear / Gear T-Level column labeled with that class (e.g. `Deflub ( PAL )` or `Deflub ( WAR )`), even when other spell files for the same character exist in the folder. Only the files you add to the export are used for persona pairing when any MissingSpells files are selected.

### Changed

- Auto-discovered spell files (inventory only, no MissingSpells in the file list) still omit Crew Gear when multiple classes share one inventory Output log.

## [1.7.1] - 2026-05-24

### Fixed

- Crew Gear and Gear T-Level no longer show columns for personas that share one inventory Output log with other spell files; equipped gear reflects only the active persona when the Output log was generated. Spell tabs still include every selected MissingSpells class. Use subfolders with separate inventory Output logs per persona for multi-class gear tracking.

## [1.7.0] - 2026-05-24

### Changed

- **Spell-driven persona pairing:** inventory files always use `CharacterName_server-Inventory.txt` (no class suffix); MissingSpells filenames are the sole source of class/persona identity
- Multiple MissingSpells files for one character in the same folder now produce multiple persona columns sharing one inventory Output log (no rename required)
- Subfolder layout supported: standard inventory filename co-located with each persona’s spell file (e.g. `PAL/Deflub_bristle-Inventory.txt` + `PAL/Deflub_bristle-PAL-MissingSpells.txt`)

## [1.6.0] - 2026-05-24

### Added

- **Alternate persona support:** multiple inventory Output logs per character when filenames include an optional class suffix (e.g. `Deflub_bristle-PAL-Inventory.txt`), paired with matching `*-CLASS-MissingSpells.txt` files; Excel columns show `Deflub ( PAL )` and `Deflub ( SHD )` side by side
- Warning when multiple MissingSpells files exist for one character but the inventory file lacks a class suffix (rename inventory using the class from the spell log)

## [1.5.0] - 2026-05-21

### Added

- Character class abbreviation in Excel column headers and spell sheets (e.g. `Deflub ( PAL )`), resolved from matching `*-CLASS-MissingSpells.txt` files in the inventory folder or `SpellData` subfolder

## [1.4.0] - 2026-05-21

### Changed

- Default export filename uses the character name when only one inventory Output log is selected (e.g. `Deflub_Crew Inventory.xlsx`); multi-character exports still use the server display name (e.g. `Bristlebane_Crew Inventory.xlsx`)

### Fixed

- Equipped Resonant Fracture (SoR-R2) gear is no longer misclassified as Evolver when the final augment slot appears in the inventory Output log; tier codes and Fracture coloring now take precedence over Evolver detection

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
