# How to Use — Inventory Parser

Turn your raid’s EverQuest inventory dumps into one Excel workbook (and optionally an interactive HTML report): who is wearing what, gear tier level per slot, optional missing Rank III spell runes, and (optionally) achievement collection progress.

The app version is shown in the window title and under **Help → About**. Standalone `.exe` builds include the same version in Windows file properties (right-click the exe → Properties → Details).

---

## What you need

### Getting dumps in-game

On each character, run these chat commands in EverQuest:

| Command | Creates |
|---------|---------|
| `/outputfile inventory` | Inventory dump (`*-Inventory.txt`) |
| `/outputfile missingspells` | Missing spells log (`*-MissingSpells.txt`) |
| `/outputfile achievements` | Achievement dump (`*-Achievements.txt`) |

EQ writes the files to your **`EverQuest/Logs`** folder (or the path your client uses for `/outputfile`). Copy those `.txt` files into one folder for the parser — each character needs their own inventory file; add spell and/or achievement files when you want those tabs.

### Inventory dumps (required)

At least one file named like:

`CharacterName_server-Inventory.txt`

Example: `Deflub_bristle-Inventory.txt`

Tab-separated text from `/outputfile inventory`. One file per character (`CharacterName_server-Inventory.txt`). The filename never includes class. The dump reflects **equipped items for the active persona only**.

**Alternate personas:** EQ’s Alternate Persona system lets one character swap class while sharing bank, bags, and other data. Class is defined **only** by the MissingSpells filename (`CharacterName_server-CLASS-MissingSpells.txt`).

**Same folder:** one inventory plus MissingSpells file(s). Add the spell file for the active persona to get a Crew Gear column labeled with that class. If you add only the inventory and multiple spell files are auto-discovered, Crew Gear is skipped (spell tabs only).

**Subfolders (separate worn gear per persona):** each persona’s folder contains the standard inventory name plus its spell file — e.g. `PAL/Deflub_bristle-Inventory.txt` + `PAL/Deflub_bristle-PAL-MissingSpells.txt`.

### Missing Spells logs (optional)

Files named like:

`CharacterName_server-CLASS-MissingSpells.txt`

Example: `Healub_bristle-CLR-MissingSpells.txt`

From `/outputfile missingspells`. One line per spell: `level` + tab + `spell name`. Only **Rk. III** lines are counted. The **CLASS** in the filename is the only way the parser knows a character’s class or persona.

You can put spell files:

- In the **same folder** as the inventory dumps, or  
- In a subfolder named **`SpellData`** next to those dumps

You may also add spell files directly in the app with **Add files…** (you still need at least one inventory file to build the workbook).

### Achievement dumps (optional)

Files named like:

`CharacterName_server-Achievements.txt`

Example: `Shamlub_xegony-Achievements.txt`

From `/outputfile achievements`. Tab-separated text with section headers (`Expansion: Collections`, `General: Advancement`, etc.) and status lines (`C` completed, `I` incomplete).

You can put achievement files:

- In the **same folder** as the inventory dumps, or  
- In a subfolder named **`AchievementData`** next to those dumps

The **Missing Collections** tab lists collection items still needed (`owned/total` progress under **Collections** sections). **Achievement Summary** counts completed vs incomplete top-level achievements per section.

---

## Quick start (GUI)

1. **In EQ:** on each toon, `/outputfile inventory` and (optional) `/outputfile missingspells`; copy the `.txt` files into one folder.

2. **Run the app**
   - Double-click **`run_gui.bat`**, or  
   - Double-click **`dist\InventoryParser.exe`** after building (see [Building the .exe](#building-the-exe))

3. **Add your files**
   - **Add files…** — pick one or more `*-Inventory.txt`, `*-MissingSpells.txt`, and/or `*-Achievements.txt` files  
   - **Add folder…** — load every matching file in a folder at once  

4. **Options** (optional)
   - **Include** — `all`, `visible`, or `non_visible` slots on the gear sheets  
   - **Include missing spells** — checked automatically when matching spell files are found; uncheck to skip spell tabs  
   - **Include achievements** — checked automatically when matching achievement files are found; uncheck to skip achievement tabs  
   - **Also generate HTML report** — writes a `{prefix}_Crew Inventory.html` file next to the Excel workbook (open in your browser; no server needed)  

5. **Output**
   - Default save location: **Downloads\{Server}_Crew Inventory.xlsx** (server slug from your inventory, MissingSpells, or `eqlog_*` files — e.g. `Bristlebane_Crew Inventory.xlsx` from `*_bristle-Inventory.txt`)  
   - Use **Browse…** to pick another path  

6. Click **Generate Excel**

If Excel already has the file open, the app saves as `Crew Inventory_1.xlsx`, etc.

---

## Reading the workbook

The file uses a **dark theme** (black background, light text). Item names link to [EQ Resource](https://items.eqresource.com/) when the dump includes item IDs.

### Crew gear

- One **column per character**, one **row per equipped slot**  
- Rows are grouped **visible** gear first, then **non-visible**  
- **Colors** show gear set (Fracture, Rebellion, Evolver, etc.) — see the legend on the sheet (rows 26–35) or **Help → Gear tiers & slots** in the app  
- **Purple** = Evolver (special augment slot, not the “6” in the Slots column)

### Gear T-Level

Same layout as Crew gear, but cells show **what tier is equipped** in each slot:

| Cell value | Meaning |
|------------|---------|
| *(blank)* | Empty slot |
| `SOR-R2` | Shattering of Ro R2 (Resonant Fracture) |
| `Evolver` | Evolver item (final augment row in dump) |
| `SOR-R1`, `TOB-R2`, `LS-G2`, etc. | Expansion tier code (`SOR`, `TOB`, `LS`, `NoS` + `G` group or `R` raid + tier number) |
| `???` | Equipped but not recognized (e.g. Legacies Lost, Selenelion) |

See the legend on the Gear T-Level sheet for the full code list.

The **Secondary** row only appears if someone had a secondary weapon on the gear sheet.

### Missing Runes *(if enabled)*

How many Minor / Lesser / Median / Greater / Glowing runes each character still needs, by level band (121–125 and 126–130).

### Spell List *(if enabled)*

Every missing **Rk. III** with character, level band, level, rune tier, and spell name. Use Excel filters to sort by character or rune type.  

Level bands that count runes today:

| Levels | Expansions | Rk. III rune item |
|--------|------------|-------------------|
| 121–125 | Laurion's Song (LS), The Outer Brood (ToB) | `{Tier} Emblem of the Forge` (LS); `Energized {Tier} Engram` (ToB) |
| 126–130 | Shattering of Ro (SoR) | `{Tier} Mirrorshard of Relic` |

`{Tier}` = Minor, Lesser, Median, Greater, or Glowing (one per spell level).

Older bands (111–120) are in config but not shown until enabled in `spell_rune_bands.json`.

### Missing Collections *(if enabled)*

Every incomplete collection item under a **Collections** section: character, expansion/category, zone (from the collection name), collection name, missing item, progress, which crew member has the item in inventory (**Char Has**), and total needed.

### Achievement Summary *(if enabled)*

Top-level achievement counts per section (expansion or category): completed, incomplete, total, and completion percentage.

### Raid Achievements *(if enabled)*

Incomplete raid **objectives** from each expansion’s **Raids** section. Columns: Character, Expansion, Raid, Objective. Expansions show release year (e.g. `Shattering of Ro (2025)`) and rows are sorted **newest to oldest**; use Excel filters on **Expansion** to narrow the list.

### HTML report *(optional)*

When **Also generate HTML report** is checked (or **`--also-html`** on the CLI), the app saves `{prefix}_Crew Inventory.html` next to the `.xlsx` file. Double-click to open in Chrome, Edge, Firefox, etc.

- Same tabs as Excel (omitted when empty, same rules as the workbook)
- **Search**, **sort** (click column headers), **Character** and **Expansion** filters on table tabs
- Gear-set and tier colors match the Excel theme; item names link to EQ Resource

No Python or web server is required to view the HTML file.

---

## Tips

- **Whole raid in one folder** — use **Add folder…** after everyone drops dumps in the same directory.  
- **Spell files in SpellData** — keeps inventory folder tidy; the app finds them automatically.  
- **Achievement files in AchievementData** — same pattern for `/outputfile achievements` dumps.  
- **Status bar** — shows how many inventory, MissingSpells, and achievement files are loaded.  
- **Remove / Clear all** — fix the file list before regenerating.  
- **Warnings** — if a character has inventory but no spell file, you’ll get a message after export; the workbook still builds.

---

## Command line (optional)

From the `Inventory Parser` folder:

```powershell
py -3 -m pip install -e .
py -3 -m inventory_parser --folder "D:\EQ Dumps" -o "D:\EQ Dumps\Crew Inventory.xlsx"
```

Skip the spell tabs:

```powershell
py -3 -m inventory_parser --folder Examples -o out.xlsx --no-spells
```

Skip the achievement tabs:

```powershell
py -3 -m inventory_parser --folder Examples -o out.xlsx --no-achievements
```

Also write an interactive HTML report (same folder, same name stem):

```powershell
py -3 -m inventory_parser --folder Examples -o out.xlsx --also-html
```

Only visible slots:

```powershell
py -3 -m inventory_parser --folder Examples -o out.xlsx --slots visible
```

---

## Building the .exe

Run **`build_exe.bat`** inside the **`Inventory Parser`** folder (not another project’s batch file).

Output: `Inventory Parser\dist\InventoryParser-<version>.exe`

Copy that `.exe` to any Windows PC; Python does not need to be installed there.

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
py -3 scripts\sign_exe.py dist\InventoryParser-1.7.5.exe
```

(with the same environment variables set).

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| “Add at least one *-Inventory.txt” | Spell files alone are not enough — add inventory dumps. |
| Spell tabs empty | Confirm spell file names match `Name_server-CLASS-MissingSpells.txt` and character names match inventory files. |
| Achievement tabs empty | Confirm achievement file names match `Name_server-Achievements.txt` and character/server match inventory files. |
| Checkbox for spells is grayed out | No inventory files in the list yet. |
| “Permission denied” / save failed | Close the workbook in Excel and try again. |
| Wrong characters in columns | Each inventory file should be one character; check filenames. |

---

## More detail

Technical reference, development setup, and config files: **[README.md](README.md)**
