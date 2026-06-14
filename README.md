# Inventory Parser

EverQuest tool that builds a **dark-themed Excel workbook** from team inventory dumps: equipped gear by slot, gear tier level tracking, and optional missing Rank III spell / rune and achievement reports. Optionally writes a matching **interactive HTML report** you open in any browser.

**Version:** see `src/inventory_parser/__init__.py` (`__version__`). Check in the GUI (**Help → About**), CLI (`--version`), or `py -3 -m inventory_parser --version`.

**New users:** start with **[HowToUse.md](HowToUse.md)** — step-by-step GUI instructions, file naming, and how to read each sheet.

**Changes:** [CHANGELOG.md](CHANGELOG.md)

## Features

| Feature | Description |
|---------|-------------|
| Multi-character export | One column per character (or persona) from `*-Inventory.txt` dumps |
| Slot layout | Visible slots first, then non-visible; filter to all / visible / non-visible |
| Gear set colors | Semantic tier buckets on **Team Gear** and **Gear T-Level** (green / yellow / orange / red / purple); legend on-sheet, HTML footer, and GUI Help |
| EQ Resource links | Item names hyperlink using item IDs from dumps |
| **Gear T-Level** | Expansion tier codes per slot (`SOR-R2`, `TOB-R2`, etc.); blank = empty; `Evolver` = Evolver item |
| **Missing Runes** / **Missing Spells** | Optional tabs: rune count matrix and missing **Rk. III** spell list |
| **Rune Inventory** | On-hand raid rune counts (NoS / LS / ToB / SoR) from inventory dumps — no spell file required |
| **Achievements** | Optional Missing Collections, Achievement Summary, and Raid Achievements tabs |
| **Unmade Gear** | Craft mats and T1 containers in General bags that still upgrade a slot |
| **HTML report** | Optional self-contained `{Server}_Team Inventory.html` — sidebar navigation, search, filters, sort (CLI: `--also-html`; GUI: **HTML** chip, on by default) |
| File picker | Accepts inventory, spell, and achievement dumps; folder scan |

## Requirements

- **Python 3.10+** (for running from source)
- Dependencies: **openpyxl** and **Pillow** (installed via `pip install -e .`)
- **Windows** for the GUI and PyInstaller `.exe` build

## Input file formats

Generate dumps in-game (per character):

```
/outputfile inventory
/outputfile missingspells
```

Files are written to the client’s log/output directory; copy them into a folder for the parser.

### Inventory (required)

- **In-game:** `/outputfile inventory`  
- **Pattern:** `CharacterName_server-Inventory.txt`  
- **Example:** `Deflub_bristle-Inventory.txt`  
- Tab-separated rows: slot, item name, item ID, count, etc.

Inventory filenames always use the character name only (`CharacterName_server-Inventory.txt`). The dump snapshots **equipped items for whichever persona was active** when `/outputfile inventory` was run.

**Alternate personas — two folder layouts:**

1. **Same folder:** one `Deflub_bristle-Inventory.txt` plus MissingSpells file(s). **Add the MissingSpells file for the active persona** to get a Team Gear column labeled with that class (e.g. `Deflub ( WAR )`). If you add only the inventory file and multiple spell files are auto-discovered, Team Gear is omitted (spell tabs only).

2. **Subfolder per persona (separate worn gear):** e.g. `PAL/Deflub_bristle-Inventory.txt` + `PAL/Deflub_bristle-PAL-MissingSpells.txt`, and the same for `SHD/`. Each subfolder uses the standard inventory filename; class comes from the spell file only.

### Missing Spells (optional)

- **In-game:** `/outputfile missingspells`  
- **Pattern:** `CharacterName_server-CLASS-MissingSpells.txt`  
- **Example:** `Healub_bristle-CLR-MissingSpells.txt`  
- Each line: `level<TAB>spell name`  
- Only lines containing **`Rk. III`** are included in the report  
- The **CLASS** segment in the filename is the **only** source of persona/class identity (inventory filenames never include class)

**Discovery order** for spell files matching an inventory dump:

1. Paths explicitly added via **Add files…** or CLI file list (when any MissingSpells files are selected, only those are used — other spell files in the folder are ignored)
2. Same folder as the inventory file (when no MissingSpells files are in the export list)
3. `SpellData/` subfolder under that folder

At least one inventory file is required to generate a workbook.

## Excel workbook

Default output name: **`{Server}_Team Inventory.xlsx`** (e.g. `Bristlebane_Team Inventory.xlsx` from the `bristle` slug in `*_bristle-Inventory.txt`, `*-MissingSpells.txt`, or `eqlog_*_bristle.txt`; GUI defaults to Downloads).

### Team Gear

- Rows = equipped slots (sorted visible → non-visible)  
- Columns = characters  
- **Visibility** column for Excel filters  
- **Evolver** detection via augment rows (`Ear-Slot6`, `Primary-Slot5`, …) — purple fill, not the Slots column value `6`  
- Tier-bucket legend at A26–A30 (green / yellow / orange / red / purple)  

### Gear T-Level

- Same slot layout as Team Gear (Secondary row omitted unless someone had secondary equipped)  
- Cells show **tier codes** for equipped gear, e.g. `SOR-R2`, `TOB-R2`, `LS-G1`, `SOR-R1`  
- Blank = empty slot; `Evolver` = Evolver item; `???` = unrecognized gear  
- Legend on the Gear T-Level sheet lists all tier codes

### Missing Runes & Missing Spells

Included when spell files are found and the **Spells** chip is enabled (GUI) or `--no-spells` is not passed (CLI).

- **Missing Runes:** rune counts (Minor → Glowing) per character for each enabled level band  
- **Missing Spells:** Character, Levels, Level, Rune, Spell — zebra striping by character, tier/block colors, frozen header, auto-filter  

Level bands with `"count_runes": true` in config (current defaults):

| Levels | Expansions | Rk. III rune item |
|--------|------------|-------------------|
| 121–125 | LS, ToB | `{Tier} Emblem of the Forge` (LS); `Energized {Tier} Engram` (ToB) |
| 126–130 | SoR | `{Tier} Mirrorshard of Relic` |

`{Tier}` is Minor, Lesser, Median, Greater, or Glowing (one per level; matches the Missing Runes rows). Examples: *Minor Emblem of the Forge*, *Energized Glowing Engram*, *Median Mirrorshard of Relic*.

Configure bands in `src/inventory_parser/data/spell_rune_bands.json` (`turn_in_theme` = rune family shown on the Missing Runes sheet). Add a new block with `"count_runes": true` for future level caps without code changes.

### Rune Inventory

Included automatically when inventory dumps contain matching raid rune items (no spell file required).

- **Rune Inventory:** on-hand counts (Minor → Glowing) per character for four families — NoS `{Tier} Symbol of Shar Vahl`, LS `{Tier} Emblem of the Forge`, ToB `Energized {Tier} Engram`, SoR `{Tier} Mirrorshard of Relic`
- Scans **General**, **Bank**, and **Shared Bank**; blank cells when count is zero; tab omitted when the team has none
- Inert and Covariant Engrams are excluded (ToB counts **Energized** engrams only)

Configure families in `src/inventory_parser/data/spell_rune_inventory.json`.

Official spell lists (Rank 1 vendors, Rank 2/3 turn-in items) on EQ Resource:

- [Shattering of Ro (SoR)](https://sor.eqresource.com/spells.php) — levels 126–130  
- [The Outer Brood (ToB)](https://tob.eqresource.com/spells.php) — levels 121–125  
- [Laurion's Song (LS)](https://ls.eqresource.com/spells.php) — levels 121–125  

### HTML report *(optional)*

When the **HTML** chip is enabled (GUI default) or **`--also-html`** is passed (CLI), the app writes `{prefix}_Team Inventory.html` beside the `.xlsx` file. Open it in Chrome, Edge, Firefox, etc. — no Python or web server required.

| Area | What you get |
|------|----------------|
| **Sidebar** | EQ logo, Lucide-style section icons (Team Gear, Gear T-Level, Missing Runes, Missing Spells, Rune Inventory, Unmade Gear, achievements…), **Character filter** chips below the nav |
| **Main header** | `{Server} Team Inventory`, character count, generation date |
| **Toolbar** | Search (keeps focus while typing); **Visible slots** on gear tabs; **Character** / **Level range** / **Rune type** / **Expansion** dropdowns on table tabs; **Expansion** on Rune Inventory (NoS / LS / ToB / SoR) |
| **Gear tables** | Color-coded cells, sticky Slot column, EQ Resource links |
| **Footer** | Gear-tier color legend (Team Gear tab) |

Same sections as Excel — omitted when empty, using the same rules as the workbook.

## GUI

Unified **dark-themed** window: **Team characters** roster, **Slots** / **Output** cards, pill-shaped buttons, and chip toggles for export options.

```powershell
cd "Inventory Parser"
py -3 -m pip install -e .
```

Double-click **`run_gui.bat`**, or:

```powershell
py -3 -m inventory_parser.gui
```

Or after install: `inventory-parser-gui`

1. **Add files** / **Add folder** — inventory and/or MissingSpells / achievement files  
2. **Slots** filter; **Spells**, **Achievements**, and **HTML** chips (HTML on by default)  
3. Set output path → **Generate Report**  

Primary **Generate Report** (green) builds the Excel workbook and, when **HTML** is checked, a matching `.html` file. **Add files** (blue), **Add folder** (teal), utility buttons (ghost), **Browse…** (teal). **Help** (header) → gear tier colors and About. EQ icon in the title bar and header.

## Command line

```powershell
py -3 -m inventory_parser --folder Examples -o "Examples/Team Inventory.xlsx"
py -3 -m inventory_parser Examples\Deflub_bristle-Inventory.txt -o Team.xlsx
py -3 -m inventory_parser --folder Examples -o out.xlsx --no-spells --slots visible
py -3 -m inventory_parser --folder Examples -o out.xlsx --also-html
```

| Option | Description |
|--------|-------------|
| `inventories` | One or more dump paths (inventory, spell, and/or achievement files) |
| `--folder` | Scan folder for matching dump files |
| `-o`, `--output` | Output `.xlsx` path (required) |
| `--slots` | `all` (default), `visible`, or `non_visible` |
| `--no-spells` | Omit Missing Runes and Missing Spells sheets |
| `--no-achievements` | Omit achievement sheets |
| `--also-html` | Also write `{prefix}_Team Inventory.html` next to the workbook |

Entry point: `inventory-parser` after `pip install -e .`

## Standalone executable

Run **`build_exe.bat`** inside this folder only:

```powershell
cd "Inventory Parser"
.\build_exe.bat
```

Output: `dist\InventoryParser-<version>.exe` (e.g. `InventoryParser-1.13.0.exe`; Explorer opens with the file selected when the build finishes).

`build_exe.bat` installs the package (including Pillow) and runs PyInstaller with Pillow bundled for pill-button rendering. Close any running `InventoryParser-*.exe` before rebuilding if you get “Access is denied” on the output file.

## Examples

| Path | Contents |
|------|----------|
| `Examples/*.txt` | Six sample `*-Inventory.txt` dumps |
| `Examples/SpellData/*.txt` | Matching `*-MissingSpells.txt` for several characters |

Try the GUI with **Add folder…** → `Examples`, then **Generate Report**.

## Versioning

Single source of truth:

```text
src/inventory_parser/__init__.py  →  __version__ = "x.y.z"
```

`pyproject.toml` reads that value automatically. After bumping the version, update [CHANGELOG.md](CHANGELOG.md). Build scripts use `scripts/print_package_version.py`.

## Development

```powershell
cd "Inventory Parser"
py -3 -m pip install -e ".[dev]"
py -3 -m pytest -q
py -3 -m inventory_parser --version
```

### Layout

```
Inventory Parser/
  HowToUse.md          ← user guide
  README.md            ← this file
  Discord_Instructions.txt
  run_gui.bat
  build_exe.bat
  Examples/
  backup/              ← pre-redesign snapshots (GUI, HTML)
  src/inventory_parser/
    cli.py gui.py html_export.py team_report.py pill_button.py gui_theme.py …
    data/team_report.html spell_rune_bands.json
  tests/
```

## License

Part of the user’s Cursor Projects workspace; no separate license file in-tree.
