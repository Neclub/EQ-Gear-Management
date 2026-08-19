# How to Use — EQ Gear Management (EQGM)

Turn your raid’s EverQuest inventory files into one Excel workbook (and optionally an interactive HTML report): who is wearing what, gear tier level per slot, unmade craft mats, optional missing Rank III spell runes, optional achievement collections/quests/raid progress, optional Type 7/8 aug recommendations, and optional current-expansion Raid BiS.

Built for **EverQuest Live** only (not TLP or progression). Gear, runes, and related tracking go back as far as **Laurion's Song**.

The app version is shown in the window title and under **Help → About EQGM**. **Help → Check for Updates** compares that version to the latest GitHub Release. Standalone `.exe` builds include the same version in Windows file properties (right-click the exe → Properties → Details), with company **Lubworks**.

---

## What you need

### Getting output files in-game

On each character, run these chat commands in EverQuest:

| Command | Creates |
|---------|---------|
| `/outputfile inventory` | Inventory file (`*-Inventory.txt`) |
| `/outputfile missingspells` | Missing spells file (`*-MissingSpells.txt`) |
| `/outputfile achievements` | Achievement file (`*-Achievements.txt`) |

EQ writes the files to your **`EverQuest/Logs`** folder (or the path your client uses for `/outputfile`). Copy those `.txt` files into one folder for the app — each character needs their own inventory file; add spell and/or achievement files when you want those tabs.

### Inventory files (required)

At least one file named like:

`CharacterName_server-Inventory.txt`

Example: `CharN_bristle-Inventory.txt`

Tab-separated text from `/outputfile inventory`. The file reflects **equipped items for the active persona only**.

You can also use class-tagged inventory names (same pattern as MissingSpells), for example after renaming exports or if the client names them this way:

`CharacterName_server-CLASS-Inventory.txt`

Example: `CharN_bristle-PAL-Inventory.txt`

**Alternate personas:** EQ’s Alternate Persona system lets one character swap class while sharing bank, bags, and other data. Each persona’s worn gear can be tracked as its own Team Gear column when you have a separate inventory file per class. Achievements and collections are shared across personas — they appear once per character, not once per class column.

**Class-tagged inventories (preferred for personas):** put `CharacterName_server-CLASS-Inventory.txt` files in the same folder with matching `CharacterName_server-CLASS-MissingSpells.txt` files. Each class file becomes its own column (e.g. `CharN ( PAL )`, `CharN ( SHD )`). If any class-tagged inventory exists for a character, the generic `CharacterName_server-Inventory.txt` for that character is ignored.

**Same folder with only a generic inventory:** one inventory plus MissingSpells file(s). Add the spell file for the active persona to get a Team Gear column labeled with that class. If you add only the inventory and multiple spell files are auto-discovered, Team Gear is skipped (spell tabs only).

**Subfolders (also supported):** each persona’s folder contains the standard inventory name plus its spell file — e.g. `PAL/CharN_bristle-Inventory.txt` + `PAL/CharN_bristle-PAL-MissingSpells.txt`. Same-folder class-tagged names are preferred when available.

**How class is determined:** reports label each column from the **worn Chest (breastplate)** in that inventory file (looked up on raidloot, then EQ Resource, and cached). MissingSpells and class-tagged inventory filenames still pair personas and are used when the chest is empty or the lookup cannot name a class.

### Missing Spells files (optional)

Files named like:

`CharacterName_server-CLASS-MissingSpells.txt`

Example: `Healub_bristle-CLR-MissingSpells.txt`

From `/outputfile missingspells`. One line per spell: `level` + tab + `spell name`. Only **Rk. III** lines are counted. The **CLASS** in the MissingSpells filename identifies the persona for pairing files; class-tagged inventory filenames use the same abbreviation. Column labels and useful-spell matching prefer the worn Chest class when it can be resolved.

You can put spell files:

- In the **same folder** as the inventory files, or  
- In a subfolder named **`SpellData`** next to those files

You may also add spell files in the same folder as inventory files (the **EQ Folder** picker groups them per character). You still need at least one inventory file to build the workbook.

### Achievement files (optional)

Files named like:

`CharacterName_server-Achievements.txt`

Example: `Shamlub_xegony-Achievements.txt`

From `/outputfile achievements`. Tab-separated text with section headers (`Expansion: Collections`, `General: Advancement`, etc.) and status lines (`C` completed, `I` incomplete).

You can put achievement files:

- In the **same folder** as the inventory files, or  
- In a subfolder named **`AchievementData`** next to those files

The **Missing Collections** tab lists collection items still needed (`owned/total` progress under **Collections** sections). **Quests** lists unfinished Mercenary and Partisan zone quest lines (`Done` / `Missing` per quest). **Achievement Summary** counts completed vs incomplete top-level achievements per section. Achievement files are named by character only (no class segment); with multiple persona inventories, those tabs still list each character once.

---

## Quick start (GUI)

The app uses a **dark HTML interface** (pywebview + WebView2) with a split-pane setup screen. When HTML export is selected, the saved report opens in your default browser after generation; the setup screen stays open.

**Setup layout:**

| Area | Contents |
|------|----------|
| **Left** | **Team characters** roster with class icons; **EQ Folder** below the list |
| **Right (top)** | **Export options** — Slots dropdown; **Spells**, **Achievements**, **Type 7/8 Augs**, and **Raid BiS** chips |
| **Right (bottom)** | **Output folder** path and **Browse…**; **Up** / **Down** / **Remove** / **Clear** for the roster |
| **Footer** | Status line; **Excel** / **HTML** / **Both** output chips; **Generate Report** |

The main window grows (within the Windows work area, above the taskbar) so Export options stay fully visible, including **Include Anniversary augs**.

**Requirements:** Windows 10/11 with **WebView2** (Microsoft Edge runtime — usually already installed).

1. **In EQ:** on each character, `/outputfile inventory` and (optional) `/outputfile missingspells`; copy the `.txt` files into one folder.

2. **Run the app**
   - Double-click **`run_gui.bat`**, or  
   - Double-click **`dist\EQGM-<version>.exe`** after building (see [Building the .exe](#building-the-exe))

3. **Add your files**
   - **EQ Folder** (under the roster) — pick a folder; in the picker, check the characters you want (optional **Server** filter), then **Add selected**. Inventory, MissingSpells, and Achievements files are grouped per character.

4. **Manage the roster** (optional)
   - **Up** / **Down** — change character column order in Excel and HTML (including Unmade Gear row order)  
   - **Remove** — take the selected character off the export list  
   - **Clear** — empty the roster and start over  

5. **Options** (optional)
   - **Slots** dropdown — `all`, `visible`, or `non_visible` on the gear sheets  
   - **Spells** chip — checked automatically when matching spell files are found; uncheck to skip spell tabs
   - **Achievements** chip — checked automatically when matching achievement files are found; uncheck to skip achievement tabs
   - **Type 7/8 Augs** chip — on by default when inventories are loaded; uncheck to skip type 7/8 aug sheets (no catalog fetch). When on, optional **Include Anniversary augs** appears, plus **Advanced weights** for a single-character roster. Artisan's Prize is recommended for Ear when it is in the inventory file. An equipped Velium Empowered Gem of Freezing is kept as a must-have and placed in the legal slot with the best stat trade-off. Only augs that fit type 7/8 holes are recommended (type 5 and similar are excluded). Generate shows a progress bar while sockets and catalogs are fetched.
   - **Raid BiS** chip — on by default when inventories are loaded; uncheck to skip the Raid BiS sheet and catalog fetch. Compares equipped armor and jewelry to current-expansion raid T1 and T2 (weapons are shown but not scored). MAG/BST/NEC keep a pet-focus ear. The first run needs network access to EQ Resource.

6. **Output**
   - Default save location: **Downloads\{Server}_Team Inventory.xlsx** (server slug from your inventory, MissingSpells, or `eqlog_*` files — e.g. `Bristlebane_Team Inventory.xlsx` from `*_bristle-Inventory.txt`)  
   - Use **Browse…** to pick another path  
   - **Excel** / **HTML** / **Both** chips next to **Generate Report** — choose workbook only, HTML only, or both (default **Both**). The choice is remembered for next time.

7. Click **Generate Report** — when HTML is included, the saved `.html` file opens in your default browser. The setup screen stays open.

If Excel already has the file open, the app saves as `Team Inventory_1.xlsx`, etc.

---

## Reading the workbook

The file uses a **dark theme** (black background, light text). Item names link to [EQ Resource](https://items.eqresource.com/) when the inventory file includes item IDs.

### Team Gear

- One **column per character**, one **row per equipped slot**  
- Rows are grouped **visible** gear first, then **non-visible**  
- **Colors** show tier bucket (green / yellow / orange / red / purple) — same rules as Gear T-Level; see legend on the sheet (rows 26–30) or **Help** → gear tier colors in the app  
- **Purple** = Evolver (special augment slot, not the “6” in the Slots column)

### Gear T-Level

Same layout as Team Gear, but cells show **what tier is equipped** in each slot:

| Cell value | Meaning |
|------------|---------|
| *(blank)* | Empty slot |
| `SOR-R2` | Shattering of Ro R2 (Resonant Fracture) |
| `Evolver` | Evolver item (final augment row in the inventory file) |
| `SOR-R1`, `TOB-R2`, `LS-G2`, etc. | Expansion tier code (`SOR`, `TOB`, `LS`, `NoS` + `G` group or `R` raid + tier number) |
| `???` | Equipped but not recognized after name matching and EQ Resource lookup (e.g. pre-LS expansions) |

See the legend on the Gear T-Level sheet for the full code list. Items whose names are not in the bundled patterns are looked up on EQ Resource; if the page lists an expansion and Raid/Group tier that maps to a known code, that T-code is used instead of `???`.

**Cell colors** (Team Gear and Gear T-Level — same rules):

| Color | Tier codes |
|-------|------------|
| Green | `SOR-R2` (current SoR raid) |
| Yellow | `SOR-R1`, `ANI27` |
| Orange | All `TOB-*` |
| Red | `LS-*`, `NoS-*`, `SOR-G*`, `???`, and other codes |
| Purple | `Evolver` |

Colors are muted so tier code text stays easy to read.

The **Secondary** row only appears if someone had a secondary weapon on the gear sheet.

### Missing Runes *(if enabled)*

How many Minor / Lesser / Median / Greater / Glowing runes each character still needs, grouped by the **spell expansion** each missing Rk. III spell comes from:

| Expansion | Rk. III rune item |
|-----------|-------------------|
| Laurion's Song (LS) | `{Tier} Emblem of the Forge` |
| The Outer Brood (ToB) | `Energized {Tier} Engram` |
| Shattering of Ro (SoR) | `{Tier} Mirrorshard of Relic` |

`{Tier}` = Minor, Lesser, Median, Greater, or Glowing (one per spell level). Each expansion gets its own matrix on the **Missing Runes** sheet and HTML tab — a character missing both LS and ToB spells at level 123 shows separate LS and ToB rune counts. In HTML, **Sort** reorders character columns (roster, name, class, or most missing); **Expansion** narrows to one expansion.

### Missing Spells *(if enabled)*

Every missing **Rk. III** spell (and missing **Rk. II** at levels 121–130, displayed as Rk. III) with character, level, rune tier, **expansion**, and spell name.

**Columns:** Character · Level · Rune · Expansion · Spell

Expansion is looked up from a bundled EQ Resource catalog for levels **121–130**. The same level band can mix expansions — e.g. a level 123 wizard may need Laurion's Song runes for some spells and The Outer Brood runes for others. Use Excel or HTML filters on **Expansion** or **Rune type** to narrow the list.

Missing Rk. II lines at rune-relevant levels count toward **Missing Runes** the same as Rk. III. Spells not in the catalog (gates, Mastery lines, etc.) may list with a blank expansion and are not counted on **Missing Runes**.

Older level bands (111–120) are in config but not shown until enabled in `spell_rune_bands.json`.

### Missing Useful Spells *(if enabled)*

Useful spells from [Raccoo’s curated list](https://docs.google.com/spreadsheets/d/1ZqUFZ-WTZvfcBfwu5g6GGEQroEwNLSfK1LMOdMHVHcA/htmlview) that still appear in each character’s MissingSpells file — **all levels**, not just 121–130.

**Columns:** Character · Level · Expansion · Spell · Highest RK · Comments

Matching is by class (worn Chest when known, otherwise the MissingSpells filename) against the bundled useful-spell catalog. Use Excel auto-filter or the HTML **Character** / **Expansion** dropdowns to focus on one persona. The sheet includes a credit link: **Based on "SOR - Raccoo's list of useful spells"**.

### Rune Inventory *(if runes found)*

On-hand raid spell rune items in **General**, **Bank**, and **Shared Bank** — no MissingSpells file required.

Four sections (NoS, LS, ToB, SoR), each with a tier × character matrix. Cells show the stack count when &gt; 0; otherwise blank. Inert and Covariant Engrams are not counted (ToB uses **Energized** engrams only).

| Family | Item pattern |
|--------|----------------|
| NoS | `{Tier} Symbol of Shar Vahl` |
| LS | `{Tier} Emblem of the Forge` |
| ToB | `Energized {Tier} Engram` |
| SoR | `{Tier} Mirrorshard of Relic` |

### Unmade Gear *(if mats found)*

Craft materials and T1 containers sitting in **General** bags that would still upgrade an equipped slot (SoR / ToB). Items already matched by a better-or-equal equipped tier are omitted. Rows follow the same character order as Team Gear.

### Missing Collections *(if enabled)*

Every incomplete collection item under a **Collections** section: character, expansion/category, zone (from the collection name), collection name, missing item, progress, which team member has the item in inventory (**Char Has**), and total needed. Personas of the same character share one inventory for collections — rows and **Char Has** names are once per character, not per class. In HTML, click a **Missing Item** name to copy it; a small balloon confirms it was added to the clipboard.

### Quests *(if enabled)*

Unfinished **Mercenary** and **Partisan** zone quest lines from each expansion’s **Quests** section. Fully complete lines are omitted. If a line is still in progress, every child quest is listed so you can see what is left in that zone.

**Excel columns:** Character · Expansion · Zone · Type · Quest · Status (`Done` / `Missing`)

**HTML:** each Mercenary/Partisan line is a card with the achievement title as the header (e.g. `Partisan of Arcstone, Shattered Isles`) and the child quests underneath as a checklist. Incomplete steps show an empty box; finished steps show **X**.

Expansions show release year (e.g. `Shattering of Ro (2025)`) and rows are sorted **newest to oldest**. In HTML, **Character**, **Expansion**, and **Zone** dropdowns narrow the list (expansion defaults to the current expansion). Personas of the same character share one achievement file — rows are once per character.

### Achievement Summary *(if enabled)*

Top-level achievement counts per section (expansion or category): completed, incomplete, total, and completion percentage.

### Raid Achievements *(if enabled)*

Incomplete **raid** lines from each expansion’s **Raids** section. Fully complete lines are omitted. If a line is still in progress, every child objective is listed so you can see what is left.

**Excel columns:** Character · Expansion · Raid · Event · Objective · Status (`Done` / `Missing`)

**HTML:** each raid is a card headed by the **Conqueror** line (e.g. `Conqueror of Labyrinth of Spite: Echo of Hate`). Child rows are the event achievements after the colon (Enraged, Give in to Greed, Unfocused, What It Wants). Incomplete steps show an empty box; finished steps show **X**.

Expansions show release year (e.g. `Shattering of Ro (2025)`) and rows are sorted **newest to oldest**. In HTML, **Character**, **Expansion**, and **Event** dropdowns narrow the list (expansion defaults to the current expansion; Event options follow the selected expansion).

### Type 7/8 Augs *(if enabled)*

Type 7/8 (usually inventory Slot2) recommendations vs a live EQ Resource catalog (raidloot fallback). Only augs that **fit type 7/8 holes** are recommended (type 5 and similar are excluded). Artisan's Prize is treated as owned when it appears in the inventory file. If **Velium Empowered Gem of Freezing** is equipped, it is kept and assigned to the legal slot with the best weighted trade-off against other BiS augs. Excel adds **Stat Summary**, **Augs**, **Need to Farm**, **Ranked Augs**, and **Aug Legend**. HTML adds a **Type 7/8 Augs** section with the same cards. Needs a network fetch the first time; later runs use disk cache under `%LOCALAPPDATA%\EQGM\`. Uncheck the chip to skip this entirely.

### Raid BiS *(if enabled)*

Current-expansion raid T1 and T2 armor and jewelry vs what each character is wearing, scored with the same class/slot weights as Type 7/8 augs. T1 can beat T2. MAG, BST, and NEC keep a pet-focus ear (`Enhanced Minion` or `Summoner` in the name). Primary, Secondary, Ammo, and Power Source are shown on the paperdoll but not scored. Wrist items are not Lore, so both wrist slots can recommend the same bracer.

**Excel:** a **Raid BiS** sheet with current item, recommended item, tier, and stat changes.

**HTML:** an inventory-window paperdoll (green outline = already BiS, gold = upgrade) plus a table of every scored slot. A **Character** dropdown at the top of the page filters to one persona (`Name ( CLASS )`). Stat changes list HP, Mana, the class’s primary HStat, and Spell Damage for casters.

Needs a network fetch the first time (EQ Resource raid armor/jewelry, raidloot fallback); later runs use `%LOCALAPPDATA%\EQGM\`. Item icons are cached at generate time. Uncheck the chip to skip this entirely.

### HTML report *(optional)*

When **HTML** or **Both** is selected next to **Generate Report** (default **Both**), or **`--also-html`** is passed on the CLI, the app saves `{prefix}_Team_Inventory.html` next to the Excel path stem (e.g. `Bristlebane_Team_Inventory.html`). HTML-only mode writes that file without creating a workbook. In the GUI, the `.html` opens in your default browser when generation finishes; you can also double-click it later in Chrome, Edge, Firefox, etc.

**Layout**

- **Left sidebar** — EQGM crest, gold-rail section buttons (same look as [Lub Inventory](https://neclub.github.io/Lub-Inventory/)), Lucide-style icons, then **Character filter** chips (directly under the nav, not at the bottom of the window)
- **Main area** — rounded title nameplate (e.g. `Bristlebane Team Inventory`, character count, generation date), toolbar, and the active section’s table
- **Footer** — gear-tier color legend when viewing **Team Gear**

**Sections**

Same sections as Excel (omitted when empty, same rules as the workbook): Team Gear, Gear T-Level, Missing Runes, Missing Spells, Missing Useful Spells, Rune Inventory, Unmade Gear, Missing Collections, Quests, Achievement Summary, Raid Achievements, **Type 7/8 Augs** when that chip is on, and **Raid BiS** when that chip is on.

**Filters & tools**

| Control | Where | What it does |
|---------|-------|----------------|
| **Character filter** (chips) | Sidebar | Multi-select filter for gear columns and table rows. Toggle any combination of characters/personas; **All** clears the filter. Shared-name personas show full labels (e.g. `CharN ( PAL )`). Unselected chips dim only while a filter is active |
| **Search** | Toolbar | Filters the active section (keeps keyboard focus while typing) |
| **Visible slots** | Toolbar (gear tabs) | All / Visible / Non-visible — replaces the old Visibility column in HTML |
| **Character** dropdown | Toolbar (table tabs and Raid BiS) | Filter Missing Spells, Missing Useful Spells, Raid Achievements, Missing Collections, Quests, etc. to one character; on **Raid BiS**, filter cards by `Name ( CLASS )` |
| **Rune type** | Toolbar (Missing Spells) | All / Minor / Lesser / Median / Greater / Glowing |
| **Expansion** dropdown | Toolbar (table tabs) | Filter **Missing Spells** by exact spell expansion; filter **Missing Useful Spells** by short expansion code (SOR, TOB, …); filter achievement tables by expansion (defaults to the **current expansion** on first open); on **Missing Runes** and **Rune Inventory**, filter to one expansion / rune family |
| **Zone** | Toolbar (Quests) | Filter Mercenary/Partisan rows to one zone (options follow the current Expansion filter) |
| **Event** | Toolbar (Raid Achievements) | Filter raid cards to one event (e.g. Echo of Hate). Options follow the current Expansion filter |
| **Sort** | Toolbar (Missing Runes) | Reorder character columns: roster order, name, class, or most missing (uses the Expansion filter when one is selected) |
| **Column headers** | Table | Click to sort |
| **Missing Item** | Missing Collections | Click an item name to copy it; a balloon confirms it was copied |

Gear-set and tier colors match the Excel theme. Item names link to EQ Resource.

No Python or web server is required to view the HTML file.

---

## Tips

- **Whole raid in one folder** — use **EQ Folder** after everyone copies output files into the same directory.  
- **Spell files in SpellData** — keeps the inventory folder organized; the app finds them automatically.  
- **Achievement files in AchievementData** — same pattern for `/outputfile achievements` files.  
- **Status bar** — shows how many inventory, MissingSpells, and achievement files are loaded.  
- **Up** / **Down** / **Remove** / **Clear** — under Output folder on the right; fix the roster before regenerating.  
- **Warnings** — if a character has inventory but no spell file, you’ll get a message after export; the workbook still builds.
- **Help** (top right) — gear tier colors, **Check for Updates** (compares this build to the latest GitHub Release), and **About EQGM** (shows the app version).

---

## Command line (optional)

From the `EQ Gear Management` folder:

```powershell
py -3 -m pip install -e .
py -3 -m inventory_parser --folder "D:\EQ Files" -o "D:\EQ Files\Team Inventory.xlsx"
```

Skip the spell tabs:

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --no-spells
```

Skip the achievement tabs:

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --no-achievements
```

Also write an interactive HTML report (same folder, same name stem):

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --also-html
```

Only visible slots:

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --slots visible
```

Skip Type 7/8 aug sheets (no catalog fetch):

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --no-slot2
```

Include Gem of Distant Echoes anniversary augs in Type 7/8 recommendations:

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --include-anniversary
```

Skip the Raid BiS sheet (no catalog fetch):

```powershell
py -3 -m inventory_parser --folder "D:\EQ Files" -o out.xlsx --no-raid-bis
```

---

## Building the .exe

Run **`build_exe.bat`** inside the **`EQ Gear Management`** folder (not another project’s batch file).

The batch file runs `pip install -e .` (installs **openpyxl** and **pywebview**) and PyInstaller. The GUI uses WebView2 on Windows and is bundled into the executable.

Output: `EQ Gear Management\dist\EQGM-<version>.exe`

Copy that `.exe` to any Windows PC; Python does not need to be installed there.

**Before rebuilding:** close any running `EQGM-*.exe`. If the old exe is still open, PyInstaller may fail with “Access is denied” when writing to `dist\`.

### Code signing (optional, recommended for release builds)

Unsigned PyInstaller EXEs are often flagged by antivirus as false positives. Signing with an **Authenticode** certificate helps SmartScreen and Defender trust the file.

1. Obtain a code signing certificate (`.pfx`) from a trusted CA, or install one in the Windows certificate store.
2. Install the **Windows SDK** (includes `signtool.exe`) via Visual Studio Build Tools or the standalone SDK.
3. Copy **`codesign.local.bat.example`** to **`codesign.local.bat`** (gitignored) and set either:
   - **`IP_SIGN_PFX`** + **`IP_SIGN_PASSWORD`** — path to your `.pfx` file, or
   - **`IP_SIGN_THUMBPRINT`** — SHA1 thumbprint of a cert in the Windows store
4. Run **`build_exe.bat`** as usual. After PyInstaller finishes, the batch file signs the EXE automatically.

If `codesign.local.bat` is not present, the build completes without signing (fine for local dev).

Set **`IP_SIGN_REQUIRED=1`** in `codesign.local.bat` if you want the build to fail when signing is not configured or fails.

You can also sign manually:

```powershell
py -3 scripts\sign_exe.py dist\EQGM-x.y.z.exe
```

(with the same environment variables set).

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| “Add at least one *-Inventory.txt” | Spell files alone are not enough — add inventory files. |
| `ModuleNotFoundError: No module named 'webview'` when running from source | Run `py -3 -m pip install -e .` in the project folder (installs pywebview). |
| GUI window is blank or fails to start | Install the [WebView2 runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Evergreen bootstrapper). |
| Build fails with “Access is denied” on the exe | Close any running `EQGM-*.exe`, then run **`build_exe.bat`** again. |
| Spell tabs empty | Confirm spell file names match `Name_server-CLASS-MissingSpells.txt` and character names match inventory files. |
| Achievement tabs empty | Confirm achievement file names match `Name_server-Achievements.txt` and character/server match inventory files. |
| Include chips are grayed out | No inventory files in the roster yet. |
| “Permission denied” / save failed | Close the workbook in Excel and try again. |
| Wrong characters in columns | Each inventory file should be one character; check filenames. |
| Type 7/8 Augs sheets missing or empty | Leave the **Type 7/8 Augs** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Raid BiS sheet missing or slots look empty | Leave the **Raid BiS** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| HTML looks outdated after an update | Regenerate the report. |
