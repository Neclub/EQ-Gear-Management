<p align="center">
  <img src="docs/img/eqgm-banner.png" alt="EQ Gear Management — Inventory & Augment Tracker">
</p>

# EQ Gear Management (EQGM)

Turn EverQuest inventory output files into a team **Excel workbook** and optional **HTML report** — equipped gear, tier levels, unmade craft mats, runes, spells, achievements, optional Type 7/8 aug recommendations, Type 5 aug display, Type 18/19 class suggestions, and current-expansion Raid BiS.

Built for **EverQuest Live** only (not TLP or progression). Gear, runes, and related tracking go back as far as **Laurion's Song**.

---

## Download

Product page: **[neclub.github.io/EQ-Gear-Management](https://neclub.github.io/EQ-Gear-Management/)** · Changelog: **[neclub.github.io/EQ-Gear-Management/changelog.html](https://neclub.github.io/EQ-Gear-Management/changelog.html)**

1. Open **[Releases](https://github.com/Neclub/EQ-Gear-Management/releases)** on GitHub.
2. Download **`EQGM-x.y.z.exe`** from the latest release.
3. Double-click to run. No Python install needed.

Installed copies check GitHub Releases when they open. If a newer version is available, a popup shows the current and newest versions and asks whether to download. You can also use **Help → Check for Updates**.

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

EQ writes those files to your **EverQuest Logs** folder.

### 2. Generate the report

1. Open **EQ Gear Management**.
2. Click **EQ Folder** and pick your EverQuest Logs folder; select which characters to import.
3. Drag names in **Team characters** to set column order if you want. Adjust **Export options** on the right if needed. **Browse…** under **Output folder** picks where to save; the file is always named `{Server}_Team Inventory.xlsx` (or `{Character}_…` for a single character).
4. Choose **Excel**, **HTML**, or **Both**, then click **Generate Report**.

<p align="center">
  <img src="docs/img/eqgm-setup.png" alt="EQ Gear Management setup screen" width="720">
</p>

Output: `{Server}_Team Inventory.xlsx` (and `{Server}_Team_Inventory.html` if HTML is included). When HTML is included, the report opens in your default browser.

### What you get

- **Team Gear** — equipped items by slot, color-coded by tier
- **Gear T-Level** — expansion tier codes per slot (unknown items looked up on EQ Resource); codes link to the item, hover for the name
- **Unmade Gear** — raid craft mats and T1 containers still sitting in bags
- **Missing Runes / Spells / Useful Spells** — from MissingSpells output files, including spells that were never purchased; spell names link to EQ Resource; HTML Missing Runes can sort columns (roster, name, class, most missing) and filter by expansion
- **Rune Inventory** — raid runes on hand
- **Achievements** — collections, Mercenary/Partisan quests, and raid progress (from achievement output files). Collection **Zone** comes from a `(Zone)` suffix or a `{Zone} Scavenger` grouping; in HTML, click a missing item name to copy it
- **Type 7/8 Augs** — optional type 7/8 recommendations (on by default); only augs that fit type 7/8 holes; equipped Velium Empowered Gem of Freezing is kept as a must-have; if an aug should move to another slot, **Upgrade to** lists the replacement for the hole it leaves
- **Type 5 Augs** — optional display of equipped type 5 augs and Empty holes (on by default); expansion + heroic stats; sortable HTML columns; no upgrade suggestions; link to the EQ Resource Type 5 list
- **Type 18/19 Augs** — *(work in progress)* optional per-class suggestions from the Zarax cheat sheet (on by default); pick a character to set class and see **Owned** for that inventory (with gear-slot chip when equipped); **Alternative** shows Owned + slot when equipped, otherwise the craft anvil; top unused Fortifications append to Optional; Enhancement augs under **Filler**; anniversary picks (Jubilation / Enduring Harmony) marked on the item name with non-anniversary alternatives; catalog reuses disk cache after the first fetch; full catalog view still available
- **Raid BiS** — optional current-expansion raid T1/T2 armor and jewelry vs equipped gear (on by default); Evolvers still get a Best in slot pick but are skipped for coin purchases (magenta gem on hover); gold nameplate and Character filter; enter raid coins to highlight the best vendor upgrade
- **Excel workbook** — dark theme on every sheet (shared headers, status colors, and chrome)
- **HTML report** — the same data in a browser, searchable and filterable, with collapsible sidebar groups (Gear, Spells, Augs, Quests & Achievements); Character filter chips show each name and class; the title graphic shows character count, generated date, and EQGM version

For file naming, Alternate Personas, reading each sheet, and troubleshooting, see **[HowToUse.md](HowToUse.md)**.

<p align="center">
  <img src="docs/img/eqgm-icon.png" alt="EQGM" width="160" height="160">
</p>

## License

Apache License 2.0. See [LICENSE](LICENSE).
