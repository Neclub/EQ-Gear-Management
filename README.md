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
| `/outputfile inventory` | Required — `Name_server-Inventory.txt` |
| `/outputfile missingspells` | Optional — spell/rune tabs |
| `/outputfile achievements` | Optional — achievement tabs |

Copy the `.txt` files from your EQ Logs folder into one folder on your PC.

### 2. Generate the report

1. Open **Inventory Parser** (the `.exe` or GUI below).
2. Click **EQ Folder** and pick the folder with your Output logs; select which characters to import.
3. Adjust **Export options** and **Output folder** on the right if needed.
4. Click **Generate Report**.

Output: `{Server}_Team Inventory.xlsx` (and `.html` if HTML is enabled). Multi-character HTML exports open in the app viewer; single-character exports stay on the setup screen.

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
- **Missing Runes / Missing Spells** — Rk. III tracking with spell expansion data (needs spell Output logs)
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
