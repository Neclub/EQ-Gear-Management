# Inventory Parser

EverQuest tool that builds a **dark-themed Excel workbook** from crew inventory dumps: equipped gear by slot, gear tier level tracking, and optional missing Rank III spell / rune reports.

**Version:** see `src/inventory_parser/__init__.py` (`__version__`). Check in the GUI (**Help → About**), CLI (`--version`), or `py -3 -m inventory_parser --version`.

**New users:** start with **[HowToUse.md](HowToUse.md)** — step-by-step GUI instructions, file naming, and how to read each sheet.

**Changes:** [CHANGELOG.md](CHANGELOG.md)

## Features

| Feature | Description |
|---------|-------------|
| Multi-character export | One column per character (or persona) from `*-Inventory.txt` dumps |
| Slot layout | Visible slots first, then non-visible; filter to all / visible / non-visible |
| Gear set colors | Fracture, Rebellion, Evolver, etc. on **Crew gear**; legend on-sheet and in GUI Help |
| EQ Resource links | Item names hyperlink using item IDs from dumps |
| **Gear T-Level** | Expansion tier codes per slot (`SOR-R2`, `TOB-R2`, etc.); blank = empty; `Evolver` = Evolver item |
| **Missing Runes** / **Spell List** | Optional tabs: rune count matrix and missing **Rk. III** spell list |
| File picker | Accepts `*-Inventory.txt` and `*-MissingSpells.txt`; folder scan for both |

## Requirements

- **Python 3.10+** (for running from source)
- Dependency: **openpyxl** (installed via `pip install -e .`)
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

1. **Same folder:** one `Deflub_bristle-Inventory.txt` plus MissingSpells file(s). **Add the MissingSpells file for the active persona** to get a Crew Gear column labeled with that class (e.g. `Deflub ( WAR )`). If you add only the inventory file and multiple spell files are auto-discovered, Crew Gear is omitted (spell tabs only).

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

Default output name: **`{Server}_Crew Inventory.xlsx`** (e.g. `Bristlebane_Crew Inventory.xlsx` from the `bristle` slug in `*_bristle-Inventory.txt`, `*-MissingSpells.txt`, or `eqlog_*_bristle.txt`; GUI defaults to Downloads).

### Crew gear

- Rows = equipped slots (sorted visible → non-visible)  
- Columns = characters  
- **Visibility** column for Excel filters  
- **Evolver** detection via augment rows (`Ear-Slot6`, `Primary-Slot5`, …) — purple fill, not the Slots column value `6`  
- Gear-set legend at A26–A35  

### Gear T-Level

- Same slot layout as Crew gear (Secondary row omitted unless someone had secondary equipped)  
- Cells show **tier codes** for equipped gear, e.g. `SOR-R2`, `TOB-R2`, `LS-G1`, `SOR-R1`  
- Blank = empty slot; `Evolver` = Evolver item; `???` = unrecognized gear  
- Legend on the Gear T-Level sheet lists all tier codes

### Missing Runes & Spell List

Included when spell files are found and **Include missing spells** is enabled (GUI) or `--no-spells` is not passed (CLI).

- **Missing Runes:** rune counts (Minor → Glowing) per character for each enabled level band  
- **Spell List:** Character, Levels, Level, Rune, Spell — zebra striping by character, tier/block colors, frozen header, auto-filter  

Level bands with `"count_runes": true` in config (current defaults):

| Levels | Expansions | Turn-in theme |
|--------|------------|----------------|
| 121–125 | LS, ToB | Timeless Medallion |
| 126–130 | SoR | Astral / Solar |

Configure bands in `src/inventory_parser/data/spell_rune_bands.json`. Add a new block with `"count_runes": true` for future level caps without code changes.

## GUI

```powershell
cd "Inventory Parser"
py -3 -m pip install -e .
```

Double-click **`run_gui.bat`**, or:

```powershell
py -3 -m inventory_parser.gui
```

Or after install: `inventory-parser-gui`

1. **Add files…** / **Add folder…** — inventory and/or MissingSpells files  
2. **Include** slot filter; **Include missing spells** when spell data exists  
3. Set output path → **Generate Excel**  

**Help → Gear tiers & slots** explains colors and visible vs non-visible slots.

## Command line

```powershell
py -3 -m inventory_parser --folder Examples -o "Examples/Crew Inventory.xlsx"
py -3 -m inventory_parser Examples\Deflub_bristle-Inventory.txt -o Crew.xlsx
py -3 -m inventory_parser --folder Examples -o out.xlsx --no-spells --slots visible
```

| Option | Description |
|--------|-------------|
| `inventories` | One or more dump paths (inventory and/or spell files) |
| `--folder` | Scan folder for `*-Inventory.txt` and `*-MissingSpells.txt` |
| `-o`, `--output` | Output `.xlsx` path (required) |
| `--slots` | `all` (default), `visible`, or `non_visible` |
| `--no-spells` | Omit Missing Runes and Spell List sheets |

Entry point: `inventory-parser` after `pip install -e .`

## Standalone executable

Run **`build_exe.bat`** inside this folder only:

```powershell
cd "Inventory Parser"
.\build_exe.bat
```

Output: `dist\InventoryParser.exe` (Explorer opens with the file selected when the build finishes).

## Examples

| Path | Contents |
|------|----------|
| `Examples/*.txt` | Six sample `*-Inventory.txt` dumps |
| `Examples/SpellData/*.txt` | Matching `*-MissingSpells.txt` for several characters |

Try the GUI with **Add folder…** → `Examples`, then **Generate Excel**.

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
  run_gui.bat
  build_exe.bat
  Examples/
  src/inventory_parser/
    cli.py gui.py excel_export.py …
    data/spell_rune_bands.json
  tests/
```

## License

Part of the user’s Cursor Projects workspace; no separate license file in-tree.
