# Setup Screen

The app uses a **dark HTML interface** with a split-pane setup screen. When HTML export is selected, the saved report opens in your default browser after generation; the setup screen stays open.

## Layout

| Area | Contents |
|------|----------|
| **Left** | **Team characters** roster with class icons; **EQ Folder** below the list |
| **Right (top)** | **Export options** — **Spells**, **Achievements**, **Type 7/8 Augs**, **Type 5 Augs**, **Type 18/19 Augs**, and **Raid BiS** chips |
| **Right (bottom)** | **Output folder** path and **Browse…**; **Up** / **Down** / **Remove** / **Clear** for the roster |
| **Footer** | Status line; **Excel** / **HTML** / **Both** output chips; **Generate Report** |

The main window grows (within the Windows work area, above the taskbar) so Export options stay fully visible, including **Include Anniversary augs**.

<p align="center">
  <img src="https://neclub.github.io/EQ-Gear-Management/img/eqgm-setup.png" alt="EQ Gear Management setup screen" width="720">
</p>

## Add your files

**EQ Folder** (under the roster) — pick the root of your **EverQuest** folder (not `Logs`); in the picker, check the characters you want (optional **Server** filter), then **Add selected**. Inventory, MissingSpells, and Achievements files are grouped per character.

## Manage the roster

- **Drag** names in **Team characters** — a gap opens to show where the name will land; that order is used for Excel and HTML columns (including Unmade Gear row order)
- **Up** / **Down** — move the selected character the same way
- **Remove** — take the selected character off the export list
- **Clear** — empty the roster and start over

## Export options

- **Spells** chip — checked automatically when matching spell files are found; uncheck to skip spell tabs
- **Achievements** chip — checked automatically when matching achievement files are found; uncheck to skip achievement tabs
- **Type 7/8 Augs** chip — on by default when inventories are loaded; uncheck to skip type 7/8 aug sheets (no catalog fetch). When on, optional **Include Anniversary augs** appears, plus **Advanced weights** for a single-character roster. Generate shows a progress bar while sockets and catalogs are fetched. The first run needs network; later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache.
- **Type 5 Augs** chip — on by default when inventories are loaded; uncheck to skip the Type 5 display sheet. Uses parent-item socket maps (cached with Type 7/8).
- **Type 18/19 Augs** chip — *(work in progress)* on by default when inventories are loaded; uncheck to skip Type 18/19 sheets. First run needs network; later runs reuse the `%LOCALAPPDATA%\EQGM\` search cache.
- **Raid BiS** chip — on by default when inventories are loaded; uncheck to skip the Raid BiS sheet and catalog fetch. The first run needs network access to EQ Resource; later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache.

Details for each report type: [[Gear]], [[Spells]], [[Augs]], [[Quests and Achievements]].

## Gear tier colors

Between Export options and Output folder. Click a swatch to change the five Team Gear / Gear T-Level bucket colors (color wheel). Your choices are saved under `%LOCALAPPDATA%\EQGM\` and apply the next time you open the app and when you generate Excel or HTML reports. **Reset to default** restores the built-in palette. **Help → Gear tier colors** shows the same palette (including your custom colors) with more detail.

## Output

- Default save location: **Downloads\\{Server}_Team Inventory.xlsx** (server slug from your inventory, MissingSpells, or `eqlog_*` files — e.g. `Bristlebane_Team Inventory.xlsx` from `*_bristle-Inventory.txt`). A single character uses that character’s name instead.
- Use **Browse…** to pick another folder. The file name is always the default above; it updates if you change which server/characters are loaded.
- **Excel** / **HTML** / **Both** chips next to **Generate Report** — choose workbook only, HTML only, or both (default **Both**). The choice is remembered for next time.

Click **Generate Report** — when HTML is included, the saved `.html` file opens in your default browser. The setup screen stays open.

If Excel already has the file open, the app saves as `Team Inventory_1.xlsx`, etc.

## Tips

- **Whole raid in one folder** — use **EQ Folder** after everyone copies output files into the same directory.
- **Spell files in SpellData** — keeps the inventory folder organized; the app finds them automatically.
- **Achievement files in AchievementData** — same pattern for `/outputfile achievements` files.
- **Status bar** — shows how many inventory, MissingSpells, and achievement files are loaded.
- **Warnings** — if a character has inventory but no spell file, you’ll get a message after export; the workbook still builds.
- **Help** (top right) — gear tier colors legend, **Check for Updates**, and **About EQGM** (shows the app version).
