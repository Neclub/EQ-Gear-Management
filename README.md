<p align="center">
  <img src="docs/img/eqgm-banner.png" alt="EQ Gear Management — Inventory & Augment Tracker">
</p>

# EQ Gear Management (EQGM)

Turn EverQuest inventory output files into a team **Excel workbook** and optional **HTML report** covering **Gear**, **Spells**, **Augs**, and **Quests & Achievements**.

Built for **EverQuest Live** only (not TLP or progression). Gear, runes, and related tracking go back as far as **Laurion's Song**.

---

## Download

Product page: **[neclub.github.io/EQ-Gear-Management](https://neclub.github.io/EQ-Gear-Management/)** · Changelog: **[neclub.github.io/EQ-Gear-Management/changelog.html](https://neclub.github.io/EQ-Gear-Management/changelog.html)**

1. Open **[Releases](https://github.com/Neclub/EQ-Gear-Management/releases)** on GitHub.
2. Download **`EQGM-install-x.y.z.exe`** from the latest release.
3. Run the installer (Windows may ask for administrator permission). It installs to **Program Files**, adds a Start Menu shortcut, and can optionally create a Desktop icon. No Python install needed.

Installed copies check GitHub Releases when they open. If a newer version is available, a popup asks whether to install it. **Yes** downloads the installer, launches it (Windows may ask for administrator permission), and closes EQGM so the upgrade can finish. You can also use **Help → Check for Updates**. Settings stay under `%LOCALAPPDATA%\EQGM\` across installs.

---

## How to use

### 1. Get output files in-game

On each character, run in EverQuest chat:

| Command | What it creates |
|---------|-----------------|
| `/outputfile inventory` | Required — `Name_server-Inventory.txt` |
| `/outputfile inventory CHR_Server-CLASS-Inventory.txt` | Optional — persona inventory (`Name_server-CLASS-Inventory.txt`). A hotkey per persona is suggested. |
| `/outputfile missingspells` | Optional — spell and rune tabs |
| `/outputfile achievements` | Optional — achievement tabs |

EQ writes those files to the root of your **EverQuest** folder (not the Logs subfolder).

### 2. Generate the report

1. Open **EQ Gear Management**.
2. Click **EQ Folder** and pick the root of your EverQuest folder; select which characters to import.
3. Drag names in **Team characters** to set column order if you want. Adjust **Export options** on the right if needed. Under **Gear tier colors**, click a swatch to customize Team Gear / Gear T-Level colors — they persist the next time you open the app. **Browse…** under **Output folder** picks where to save; the file is always named `{Server}_Team Inventory.xlsx` (or `{Character}_…` for a single character).
4. Choose **Excel**, **HTML**, or **Both**, then click **Generate Report**.

<p align="center">
  <img src="docs/img/eqgm-setup.png" alt="EQ Gear Management setup screen" width="720">
</p>

Output: `{Server}_Team Inventory.xlsx` (and `{Server}_Team_Inventory.html` if HTML is included). When HTML is included, the report opens in your default browser.

### What you get

Choose **Excel**, **HTML**, or **Both**. Excel uses a dark theme on every sheet. HTML is the same data in a browser — searchable and filterable, with a collapsible sidebar grouped like the sections below. Character filter chips show each name and class; the title graphic shows character count, generated date, and EQGM version. Type 7/8, Type 5, Type 18/19, and Raid BiS catalogs seed from the shared GitHub prebuilt cache on first generate (and after Clear Cache), then reuse `%LOCALAPPDATA%\EQGM\` afterward.

#### Gear *(inventory files)*

- **Team Gear** — equipped items by slot, color-coded by tier. In HTML, hover an item name for an inspect card
- **Gear T-Level** — expansion tier codes per slot (unknown items looked up on EQ Resource); codes link to the item. In HTML, hover a T-code for an inspect card; Excel shows the item name on hover
- **Unmade Gear** — raid craft mats and T1 containers still sitting in bags
- **Raid BiS** — optional current-expansion raid T1/T2 armor and jewelry vs equipped gear (on by default). Only items that class can wear are recommended. MAG/BST/NEC keep a pet-focus ear ranked by Enhanced Minion level. Evolvers still get a Best in slot pick but are skipped for coin purchases (magenta gem on hover). Gold nameplate and Character filter. Enter raid coins to highlight the best vendor upgrade.
- **Missing Ores** — how many raid-vendor ores (linings, clasps, cloths, etc.) each character still needs for Raid BiS upgrades. Same character-column matrix as Missing Runes; Evolver slots show the purple crystal and are excluded from counts and Total. Waist ore is omitted when a T2 ore belt is already equipped. Bag stock is not subtracted (see Unmade Gear). Shown when Raid BiS is on.

#### Spells *(MissingSpells files; Rune Inventory also uses bags)*

- **Missing Runes** — Minor / Lesser / Median / Greater / Glowing runes still needed, by spell expansion. HTML can sort columns (roster, name, class, most missing) and filter by expansion
- **Missing Spells** — missing Rk. III spells at 121–130, including spells that were never purchased; names link to EQ Resource
- **Missing Useful Spells** — Raccoo’s useful list still in the MissingSpells file (all levels)
- **Rune Inventory** — raid runes on hand in bags, bank, and shared bank

#### Augs *(optional; on by default)*

- **Type 7/8 Augs** — recommendations ranked by class weights (**DRU** Spell Damage first, then HWis); only augs that fit type 7/8 holes; equipped Velium Empowered Gem of Freezing is kept as a must-have; if an aug should move to another slot, **Upgrade to** lists the replacement for the hole it leaves
- **Type 5 Augs** — equipped type 5 augs and Empty holes; expansion + heroic stats; Vanquisher rewards use short labels (`Vanq ToL`, `Vanq NoS`, etc.) linked to the achievement; sortable HTML columns; no upgrade suggestions; link to the EQ Resource Type 5 list
- **Type 18/19 Augs** — per-class suggestions from the Zarax cheat sheet. Pick a character to set class and see **Owned** (with a gear-slot chip when equipped). **Alternative** shows Owned + slot when equipped, otherwise the craft anvil. Unused Fortifications append to Optional; Enhancement augs under **Filler**. Anniversary picks (Jubilation / Enduring Harmony) marked on the item name with non-anniversary alternatives. Full catalog view still available.

#### Quests & Achievements *(achievement files)*

- **Missing Collections** — incomplete collection items; **Zone** from a `(Zone)` suffix or a `{Zone} Scavenger` grouping; in HTML, click a missing item name to copy it
- **Quests** — unfinished Mercenary and Partisan zone quest lines
- **Raid Achievements** — incomplete raid event objectives
- **Hunters** — incomplete zone hunter kill lists
- **Slayer** — Megadeath checklist (A Force of Nature, Highly Decorated, Progressive); completed Megadeath still listed
- **Tradeskills** — skill levels from completed `Skill (N)` achievements; one card/row per character; Alchemy / Tinkering / Poisonmaking only when present; HTML **Achievements** chip notes levels are not live skill
- **Heroic AA** — Fortitude / Resolution / Vitality ranks; hover **F** / **R** / **V**; click a name to open EQ Resource
- **Achievement Summary** — completed vs incomplete counts per section

For file naming, Alternate Personas, reading each sheet, and troubleshooting, see the **[Wiki](https://github.com/Neclub/EQ-Gear-Management/wiki)**.

<p align="center">
  <img src="docs/img/eqgm-icon.png" alt="EQGM" width="160" height="160">
</p>

## License

Apache License 2.0. See [LICENSE](LICENSE).
