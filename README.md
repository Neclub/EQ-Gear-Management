# Inventory Parser

Turn EverQuest inventory Output logs into a team **Excel workbook** and optional **HTML report** — equipped gear, tier levels, runes, spells, and achievements.

**Latest build:** [GitHub Releases](https://github.com/Neclub/Inventory-Parser/releases)

---

## Download (recommended)

1. Open **[Releases](https://github.com/Neclub/Inventory-Parser/releases)** on GitHub.
2. Download **`InventoryParser-x.y.z.exe`** from the latest release.
3. Double-click to run. No Python install needed.

Every push to `main` builds a fresh `.exe` and uploads it to Releases automatically.

---

## Quick start

### 1. Get Output logs in-game

On each character, run in EverQuest chat:

| Command | What it creates |
|---------|-----------------|
| `/outputfile inventory` | Required — `Name_server-Inventory.txt` (or `Name_server-CLASS-Inventory.txt` for personas) |
| `/outputfile missingspells` | Optional — spell/rune tabs |
| `/outputfile achievements` | Optional — achievement tabs |

Copy the `.txt` files from your EQ Logs folder into one folder on your PC. For Alternate Personas, class-tagged inventory names (`Name_server-CLASS-Inventory.txt`) each become their own gear column; see [HowToUse.md](HowToUse.md).

### 2. Generate the report

1. Open **Inventory Parser** (the `.exe` or GUI below).
2. Click **EQ Folder** and pick the folder with your Output logs; select which characters to import.
3. Adjust **Export options** and **Output folder** on the right if needed.
4. Click **Generate Report**.

Output: `{Server}_Team Inventory.xlsx` (and `{Server}_Team_Inventory.html` if HTML is enabled). When HTML export is on, the saved `.html` file opens in your default browser; the setup screen stays open.

**Need more detail?** See **[HowToUse.md](HowToUse.md)** — file naming, alternate personas, reading each sheet, and troubleshooting.

---

## Run from source (developers)

**Requirements:** Windows, Python 3.10+

```powershell
cd "Inventory Parser"
py -3 -m pip install -e .
```

**GUI:** double-click `run_gui.bat`, or run `py -3 -m inventory_parser.web_gui`

The GUI uses **WebView2** (Microsoft Edge). It is preinstalled on most Windows 10/11 systems.

**CLI example:**

```powershell
py -3 -m inventory_parser --folder Examples -o "Team Inventory.xlsx" --also-html
```

---

## Build the `.exe` locally

```powershell
.\build_exe.bat
```

Output: `dist\InventoryParser-<version>.exe`

---

## What you get

- **Team Gear** — equipped items by slot, color-coded by tier
- **Gear T-Level** — expansion tier codes per slot
- **Missing Runes** — Rk. III rune totals grouped by spell expansion (LS / ToB / SoR; needs spell Output logs)
- **Missing Spells** — per-spell list with expansion, level, and rune tier (needs spell Output logs)
- **Missing Useful Spells** — curated useful spells still missing (Raccoo’s list × MissingSpells; needs spell Output logs)
- **Rune Inventory** — raid runes on hand (from inventory Output logs)
- **Achievements** — collection and raid progress (needs achievement Output logs)
- **HTML report** — same data in a browser, searchable and filterable

---

## Links

| | |
|---|---|
| Step-by-step user guide | [HowToUse.md](HowToUse.md) |
| Change history | [CHANGELOG.md](CHANGELOG.md) |
| Latest `.exe` | [GitHub Releases](https://github.com/Neclub/Inventory-Parser/releases) |

---

## Development

```powershell
py -3 -m pip install -e ".[dev]"
py -3 -m pytest -q
```

Bump version in `src/inventory_parser/__init__.py`, update [CHANGELOG.md](CHANGELOG.md), then push to `main` — CI builds and publishes the new release.

Refresh the level 121–130 spell expansion catalog after EQ patches:

```powershell
py -3 scripts/scrape_spell_expansions.py --cache
```

Commit the updated `src/inventory_parser/data/spell_expansions_121_130.json`.

Refresh the curated useful-spell list after updating Raccoo’s xlsx under `Examples/SpellData/`:

```powershell
py -3 scripts/convert_useful_spells.py
```

Commit the updated `src/inventory_parser/data/useful_spells.json`.
