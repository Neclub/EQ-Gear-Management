# How to Use — EQ Gear Management (EQGM)

Turn your raid’s EverQuest inventory files into one Excel workbook (and optionally an interactive HTML report): who is wearing what, gear tier level per slot, unmade craft mats, optional missing Rank III spell runes, optional achievement collections/quests/raid progress, optional Type 7/8 aug recommendations, optional Type 5 aug display, optional Type 18/19 aug catalog, and optional current-expansion Raid BiS.

Built for **EverQuest Live** only (not TLP or progression). Gear, runes, and related tracking go back as far as **Laurion's Song**.

The app version is shown in the window title and under **Help → About EQGM**. HTML reports also show it on the title graphic next to the generated date (for example `9 characters · generated 2026-08-24 · EQGM v1.34.4`), so a shared file tells you which build produced it. When the app opens, it checks the latest GitHub Release. If a newer version is available, a popup shows the current and newest versions and asks whether to download. **Yes** opens the official GitHub download in your browser; the app does not install or run the file. **Help → Check for Updates** runs the same check on demand. Standalone `.exe` builds include the same version in Windows file properties (right-click the exe → Properties → Details), with company **Lubworks**.

---

## What you need

### Getting output files in-game

On each character, run these chat commands in EverQuest:

| Command | Creates |
|---------|---------|
| `/outputfile inventory` | Inventory file (`*-Inventory.txt`) |
| `/outputfile inventory CHR_Server-CLASS-Inventory.txt` | Optional — persona inventory (`*-CLASS-Inventory.txt`). A hotkey per persona is suggested. |
| `/outputfile missingspells` | Missing spells file (`*-MissingSpells.txt`) |
| `/outputfile achievements` | Achievement file (`*-Achievements.txt`) |

EQ writes the files to the root of your **EverQuest** folder (not `Logs`). Point **EQ Folder** at that folder — each character needs their own inventory file; add spell and/or achievement files when you want those tabs.

### Inventory files (required)

At least one file named like:

`CharacterName_server-Inventory.txt`

Example: `CharN_bristle-Inventory.txt`

Tab-separated text from `/outputfile inventory`. The file reflects **equipped items for the active persona only**.

You can also write a class-tagged inventory directly (same pattern as MissingSpells) with `/outputfile inventory CHR_Server-CLASS-Inventory.txt` (a hotkey per persona is suggested):

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

From `/outputfile missingspells`. One line per spell: `level` + tab + `spell name`. Rank 1 spells that were never purchased are listed by name only (EverQuest does not write `Rk. I`). Rank is only `Rk. II` or `Rk. III`; roman numerals in the spell name (for example Yaulp XIX) are the spell line, not rank. EQGM treats never-purchased rank 1 and missing Rk. II as missing Rk. III. The **CLASS** in the MissingSpells filename identifies the persona for pairing files; class-tagged inventory filenames use the same abbreviation. Column labels and useful-spell matching prefer the worn Chest class when it can be resolved.

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

The **Missing Collections** tab lists collection items still needed (`owned/total` progress under **Collections** sections). **Zone** comes from a `(Zone)` suffix on the collection name, or from a `{Zone} Scavenger` grouping when the title has no zone. **Quests** lists unfinished Mercenary and Partisan zone quest lines (`Done` / `Missing` per quest). **Achievement Summary** counts completed vs incomplete top-level achievements per section. Achievement files are named by character only (no class segment); with multiple persona inventories, those tabs still list each character once.

---

## Quick start (GUI)

The app uses a **dark HTML interface** with a split-pane setup screen. When HTML export is selected, the saved report opens in your default browser after generation; the setup screen stays open.

**Setup layout:**

| Area | Contents |
|------|----------|
| **Left** | **Team characters** roster with class icons; **EQ Folder** below the list |
| **Right (top)** | **Export options** — **Spells**, **Achievements**, **Type 7/8 Augs**, **Type 5 Augs**, **Type 18/19 Augs**, and **Raid BiS** chips |
| **Right (bottom)** | **Output folder** path and **Browse…**; **Up** / **Down** / **Remove** / **Clear** for the roster |
| **Footer** | Status line; **Excel** / **HTML** / **Both** output chips; **Generate Report** |

The main window grows (within the Windows work area, above the taskbar) so Export options stay fully visible, including **Include Anniversary augs**.

**Requirements:** Windows 10/11 with **WebView2** (Microsoft Edge runtime — usually already installed).

1. **In EQ:** on each character, `/outputfile inventory` and (optional) `/outputfile missingspells` and `/outputfile achievements`. For a persona inventory, also run `/outputfile inventory CHR_Server-CLASS-Inventory.txt` (a hotkey per persona is suggested).

2. **Run the app**
   - Download **`EQGM-x.y.z.exe`** from [Releases](https://github.com/Neclub/EQ-Gear-Management/releases)
   - Double-click the `.exe` to open it

   If a newer GitHub Release exists, a popup shows the current and newest versions and asks whether to download.

3. **Add your files**
   - **EQ Folder** (under the roster) — pick the root of your **EverQuest** folder (not `Logs`); in the picker, check the characters you want (optional **Server** filter), then **Add selected**. Inventory, MissingSpells, and Achievements files are grouped per character.

4. **Manage the roster** (optional)
   - **Drag** names in **Team characters** — a gap opens to show where the name will land; that order is used for Excel and HTML columns (including Unmade Gear row order)
   - **Up** / **Down** — move the selected character the same way
   - **Remove** — take the selected character off the export list  
   - **Clear** — empty the roster and start over  

5. **Options** (optional)
   - **Spells** chip — checked automatically when matching spell files are found; uncheck to skip spell tabs
   - **Achievements** chip — checked automatically when matching achievement files are found; uncheck to skip achievement tabs
   - **Type 7/8 Augs** chip — on by default when inventories are loaded; uncheck to skip type 7/8 aug sheets (no catalog fetch). When on, optional **Include Anniversary augs** appears, plus **Advanced weights** for a single-character roster. Artisan's Prize is recommended for Ear when it is in the inventory file. An equipped Velium Empowered Gem of Freezing is kept as a must-have and placed in the legal slot with the best stat trade-off. Only augs that fit type 7/8 holes are recommended (type 5 and similar are excluded). Generate shows a progress bar while sockets and catalogs are fetched. The first run needs network; later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache.
   - **Type 5 Augs** chip — on by default when inventories are loaded; uncheck to skip the Type 5 display sheet. Shows equipped type 5 augs (and Empty holes) with heroic stats; no upgrade suggestions. Uses parent-item socket maps (cached with Type 7/8). Link to the EQ Resource Type 5 list is included in the report.
   - **Type 18/19 Augs** chip — *(work in progress)* on by default when inventories are loaded; uncheck to skip Type 18/19 sheets. Per-class suggestions (Primary / Optional / Filler) from the Zarax cheat sheet, matched to the EQ Resource catalog. Anniversary augs (Jubilation / Enduring Harmony) are marked and always show a non-anniversary **Alternative**; Selenelion is a craft, not anniversary. HTML defaults to Suggestions with a toolbar **Character** select (class comes from the character; **Owned** is that character’s inventory, with a gear-slot chip when the aug is currently equipped). An **Alternative** that is owned and equipped gets Owned plus a location chip; otherwise it gets the craft anvil. Full catalog is still available. Excel: **Type 18-19 Augs** + **Type 18-19 Catalog**. First run needs network; later runs reuse the `%LOCALAPPDATA%\EQGM\` search cache.
   - **Raid BiS** chip — on by default when inventories are loaded; uncheck to skip the Raid BiS sheet and catalog fetch. Compares equipped armor and jewelry to current-expansion raid T1 and T2 (weapons are shown but not scored). MAG/BST/NEC keep a pet-focus ear. HTML cards take raid coin counts to mark the best vendor ore purchase. The first run needs network access to EQ Resource; later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache.
   - **Gear tier colors** — between Export options and Output folder. Click a swatch to change the five Team Gear / Gear T-Level bucket colors (color wheel). Your choices are saved under `%LOCALAPPDATA%\EQGM\` and apply the next time you open the app and when you generate Excel or HTML reports. **Reset to default** restores the built-in palette. **Help → Gear tier colors** shows the same palette (including your custom colors) with more detail.

6. **Output**
   - Default save location: **Downloads\{Server}_Team Inventory.xlsx** (server slug from your inventory, MissingSpells, or `eqlog_*` files — e.g. `Bristlebane_Team Inventory.xlsx` from `*_bristle-Inventory.txt`). A single character uses that character’s name instead.  
   - Use **Browse…** to pick another folder. The file name is always the default above; it updates if you change which server/characters are loaded.  
   - **Excel** / **HTML** / **Both** chips next to **Generate Report** — choose workbook only, HTML only, or both (default **Both**). The choice is remembered for next time.

7. Click **Generate Report** — when HTML is included, the saved `.html` file opens in your default browser. The setup screen stays open.

If Excel already has the file open, the app saves as `Team Inventory_1.xlsx`, etc.

---

## Reading the workbook

The file uses a **dark theme** on every sheet (black chrome, light text, shared header and status colors). Item names and Gear T-Level codes link to [EQ Resource](https://items.eqresource.com/) when the inventory file includes item IDs; hover a T-code to see the item name. Missing Spells and Missing Useful Spells names link to [EQ Resource spells](https://spells.eqresource.com).

### Team Gear

- One **column per character**, one **row per equipped slot**  
- Rows are grouped **visible** gear first, then **non-visible**  
- **Colors** show tier bucket — same rules as Gear T-Level; see legend on the sheet (rows 26–30), the **Gear tier colors** panel in the app, or **Help** → gear tier colors  
- **Evolver** bucket (purple by default) = Evolver (special augment slot, not the “6” in the Slots column)

### Gear T-Level

Same layout as Team Gear, but cells show **what tier is equipped** in each slot. Tier codes link to [EQ Resource](https://items.eqresource.com/) when the inventory includes item IDs; hover a cell to see the item name.

| Cell value | Meaning |
|------------|---------|
| *(blank)* | Empty slot |
| `SOR-R2` | Shattering of Ro R2 (Resonant Fracture) |
| `Evolver` | Evolver item (final augment row in the inventory file) |
| `SOR-R1`, `TOB-R2`, `LS-G2`, etc. | Expansion tier code (`SOR`, `TOB`, `LS`, `NoS` + `G` group or `R` raid + tier number) |
| `???` | Equipped but not recognized after name matching and EQ Resource lookup (e.g. pre-LS expansions) |

See the legend on the Gear T-Level sheet for the full code list. Items whose names are not in the bundled patterns are looked up on EQ Resource; if the page lists an expansion and Raid/Group tier that maps to a known code, that T-code is used instead of `???`.

**Cell colors** (Team Gear and Gear T-Level — same rules):

| Default color | Tier codes |
|---------------|------------|
| Green | `SOR-R2` (current SoR raid) |
| Yellow | `SOR-R1`, `ANI27` |
| Orange | All `TOB-*` |
| Red | `LS-*`, `NoS-*`, `SOR-G*`, `???`, and other codes |
| Purple | `Evolver` |

Defaults are muted so tier code text stays easy to read. Change any bucket in the **Gear tier colors** panel; the new colors persist the next time you open the app and are used in new Excel and HTML reports.

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

Every missing **Rk. III** spell at levels 121–130, including missing **Rk. II** and spells that were **never purchased**, displayed as Rk. III. Columns: character, level, rune tier, **expansion**, and spell name. Never-purchased spells show a **Not Purchased** chip in HTML, or the same label after the name in Excel. Spell names link to [EQ Resource](https://spells.eqresource.com) (direct spell page when the catalog has an id; otherwise a name search).

**Columns:** Character · Level · Rune · Expansion · Spell

Expansion is looked up from a bundled EQ Resource catalog for levels **121–130**. The same level band can mix expansions — e.g. a level 123 wizard may need Laurion's Song runes for some spells and The Outer Brood runes for others. Use Excel or HTML filters on **Expansion** or **Rune type** to narrow the list.

Missing Rk. II lines and never-purchased rank 1 spells at rune-relevant levels count toward **Missing Runes** the same as Rk. III. Spells not in the catalog (gates, Mastery lines, etc.) may list with a blank expansion and are not counted on **Missing Runes**.

Older level bands (111–120) are in config but not shown until enabled in `spell_rune_bands.json`.

### Missing Useful Spells *(if enabled)*

Useful spells from [Raccoo’s curated list](https://docs.google.com/spreadsheets/d/1ZqUFZ-WTZvfcBfwu5g6GGEQroEwNLSfK1LMOdMHVHcA/htmlview) that still appear in each character’s MissingSpells file — **all levels**, not just 121–130.

**Columns:** Character · Level · Expansion · Spell · Highest RK · Comments

Matching is by class (worn Chest when known, otherwise the MissingSpells filename) against the bundled useful-spell catalog. Spell names link to EQ Resource the same way as **Missing Spells**. Use Excel auto-filter or the HTML **Character** / **Expansion** dropdowns to focus on one persona. The sheet includes a credit link: **Based on "SOR - Raccoo's list of useful spells"**.

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

Craft materials and T1 containers sitting in **General** bags (SoR / ToB). Every recognized unmade raid item is listed so you can see it is still in inventory; Equipped Tier is shown for context and does not hide rows. Rows follow the same character order as Team Gear.

### Missing Collections *(if enabled)*

Every incomplete collection item under a **Collections** section: character, expansion/category, zone (from a `(Zone)` suffix on the collection name, or from a `{Zone} Scavenger` grouping), collection name, missing item, progress, which team member has the item in inventory (**Char Has**), and total needed. Personas of the same character share one inventory for collections — rows and **Char Has** names are once per character, not per class. **Stalking Fear** (Rain of Fear) is omitted from this list. In HTML, hover **Missing Item** for a reminder that clicking a name copies it; a small balloon confirms it was added to the clipboard.

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

Type 7/8 (usually inventory Slot2) recommendations vs an EQ Resource catalog (raidloot fallback). Only augs that **fit type 7/8 holes** are recommended (type 5 and similar are excluded). Artisan's Prize is treated as owned when it appears in the inventory file. If **Velium Empowered Gem of Freezing** is equipped, it is kept and assigned to the legal slot with the best weighted trade-off against other BiS augs. Scoring uses class weights: tanks AC then HDex; melee HDex; priests (CLR, SHM) HWis; INT casters Spell Damage. **DRU** ranks Spell Damage first (weight 9) with HWis as a secondary (weight 1). Override for one character under **Advanced weights**. Excel adds **Stat Summary**, **Augs**, **Need to Farm**, **Ranked Augs**, and **Aug Legend**. HTML adds a **Type 7/8 Augs** section with the same cards. Needs a network fetch the first time; later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache instead of re-querying EQ Resource. Uncheck the chip to skip this entirely.

**Slot recommendations** compare **Current** to **Upgrade to**. Hover the **?** for a reminder that these are suggestions — some classes already sit at a stat cap. **BiS** leaves Upgrade to blank — that hole already has the suggested aug. If a note says to move an aug to another slot (Charm, Range, Feet, and similar priority holes can claim a piece sitting elsewhere), Upgrade to lists what should replace it in the hole being vacated. The destination row shows a **Move from** badge.

When a recommended aug still needs a Focus of Fortitude (Unraveling, Otherworldly, Gallant, or Focus of Uprising) or Ensanguined ore, HTML shows a **Need** or **Have** chip that links to EQ Resource. **Slot recommendations** and **Need to farm** both use those chips. Regenerating after an app update is required for older HTML files to pick this up.

### Type 5 Augs *(if enabled)*

Display-only list of what is in each type 5 hole (often inventory Slot2 on current gear, but the dump SlotN comes from the parent item’s socket map). Empty holes show as **Empty**. Columns include **Expansion** (from EQ Resource) and heroic stats (HStr through HCha) when an aug is equipped. No BiS or farm suggestions — preference only. Excel adds a **Type 5 Augs** sheet; HTML adds a **Type 5 Augs** section with **one card per character** (same gold nameplate and class badge as Raid BiS), a **Character** filter (All or one character), clickable column headers to sort, and a link to the [EQ Resource Type 5 list](https://items.eqresource.com/itemsearch.php?searchid=481762). Uncheck the chip to skip.

### Type 18/19 Augs *(if enabled — work in progress)*

Per-class **Primary** and **Optional** suggestions from the Zarax Type 18/19 cheat sheet, resolved against the EQ Resource catalog (stats / item links). This feature is still being refined. Defense-family picks are moved to Optional. The top two unused **Fortification** augs from the catalog are appended to Optional (greatest→least). Unused **Enhancement** augs are listed under **Filler** (greatest→least). If a better aug exists in the same category, type, and expansion series, that pick is used. **Anniversary** augs (Jubilation / Enduring Harmony) are marked on the item name (HTML chip / Excel highlight) and always get a non-anniversary **Alternative**. Selenelion augs are crafts, not anniversary. Non-anniversary augs show a craft (anvil) icon in HTML; click copies the name for pasting into EQ Traders or chat. Caster classes show **Mana** / **Spell Damage** instead of AC / HP. HTML: **Suggestions** view with a toolbar **Character** select (sets class; **Owned** when that character has the aug, with a location chip when it is currently equipped). An **Alternative** that is owned and equipped gets Owned plus a location chip; otherwise it gets the craft anvil. **Full catalog** view keeps lore/category filters. Excel: **Type 18-19 Augs** (suggestions per character; columns auto-sized) and **Type 18-19 Catalog**. Dual-slot ``18, 19`` → **18/19**; ``19`` only → **19**. Needs a network fetch the first time; later runs reuse `%LOCALAPPDATA%\EQGM\` catalog cache (no full EQ Resource re-search). Toggle with the Include chip or CLI `--type18` / `--no-type18`.

### Raid BiS *(if enabled)*

Current-expansion raid T1 and T2 armor and jewelry vs what each character is wearing, scored with the same class/slot weights as Type 7/8 augs. T1 can beat T2. Evolvers are not scored and may still be BiS; they still get a Best in slot pick and show vendor cost, but that slot is skipped when choosing coin purchases. A pulsing magenta gem next to the equipped item marks an Evolver on hover. MAG, BST, and NEC keep a pet-focus ear (`Enhanced Minion` or `Summoner` in the name). Primary, Secondary, Ammo, and Power Source are shown on the paperdoll but not scored. Wrist items are not Lore, so both wrist slots can recommend the same bracer. An item already equipped is not suggested as BiS for a different slot.

**Waist belts** are a personal choice. The HTML report’s **Best in slot** column shows a dropdown of the three best-statted raid belts — one each for **Overdrive Punch**, **Treaded Boon of Potential**, and **Crippling Slicer**. The default selection is the highest class-weighted of those three; picking another belt updates that row’s **Stat changes**, the character total, and the paperdoll. A **?** next to the Waist stat changes explains the three-belt choice on hover. Excel shows the class-weighted default and notes that Waist is a personal choice (use the HTML report to compare).

**Raid coins:** each HTML character card has a coin box on the right, labeled with the current expansion’s raid currency (**Forgotten Ruined Coin** for Shattering of Ro). That value is only used for that character. Best in slot rows show a coin after the recommended item (including Evolver slots); hover it for the raid vendor cost — T2 recommendations use the slot’s vendor **ore** (Fractured lining/clasp/fastener); T1 jewelry that is sold on the vendor shows that item’s cost. Enter how many coins you have: the report marks the best affordable upgrade with a **Best Purchase** bubble. If you can afford more than one, it picks the combination that gains the most weighted stats for the coins you have. Evolver slots are not included in those purchase picks.

**Excel:** a **Raid BiS** sheet with current item, recommended item, tier, vendor cost/item, and stat changes.

**HTML:** an inventory-window paperdoll (green outline = already BiS, gold = upgrade) plus a table of every scored slot. Character names use a gold nameplate with a class badge. Hover **Raid BiS** for scoring notes (current raid gear, Evolvers, waist choice, and coins). A **Character** dropdown at the top of the page filters to one persona (`Name ( CLASS )`). Stat changes list HP, the class’s primary HStat, AC for tanks (WAR/PAL/SHD), Mana except for WAR/ROG/MNK/BER, and Spell Damage for casters.

Needs a network fetch the first time (EQ Resource raid armor/jewelry, raidloot fallback); later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache instead of re-querying EQ Resource. Item icons are cached at generate time. Uncheck the chip to skip this entirely.

### HTML report *(optional)*

When **HTML** or **Both** is selected next to **Generate Report** (default **Both**), the app saves `{prefix}_Team_Inventory.html` next to the Excel path stem (e.g. `Bristlebane_Team_Inventory.html`). HTML-only mode writes that file without creating a workbook. The `.html` opens in your default browser when generation finishes; you can also double-click it later in Chrome, Edge, Firefox, etc.

**Layout**

- **Left sidebar** — EQGM crest, collapsible section groups (**Gear**, **Spells**, **Augs**, **Quests & Achievements**), gold-rail section buttons (same look as [Lub Inventory](https://neclub.github.io/Lub-Inventory/)), Lucide-style icons, then **Character filter** chips (directly under the nav, not at the bottom of the window). Groups start collapsed; click a group heading to expand or collapse its tabs. The browser remembers which groups you leave open.
- **Main area** — rounded title nameplate (e.g. `Bristlebane Team Inventory`, character count, generation date, and EQGM version), toolbar, and the active section’s table
- **Footer** — gear-tier color legend when viewing **Team Gear**

**Sections**

Same sections as Excel (omitted when empty, same rules as the workbook), grouped in the sidebar:

- **Gear** — Team Gear, Gear T-Level, Raid BiS, Unmade Gear
- **Spells** — Missing Spells, Missing Useful Spells, Missing Runes, Rune Inventory
- **Augs** — Type 7/8 Augs, Type 5 Augs, Type 18/19 Augs (each when that chip is on)
- **Quests & Achievements** — Missing Collections, Quests, Raid Achievements, Achievement Summary

**Filters & tools**

| Control | Where | What it does |
|---------|-------|----------------|
| **Character filter** (chips) | Sidebar | Multi-select filter for gear columns and table rows. Toggle any combination of characters/personas; **All** clears the filter. Chips sit in a two-column grid and show the character name and class when known. Unselected chips dim only while a filter is active |
| **Search** | Toolbar | Filters the active section (keeps keyboard focus while typing) |
| **Visible slots** | Toolbar (gear tabs) | All / Visible / Non-visible — replaces the old Visibility column in HTML |
| **Character** dropdown | Toolbar (table tabs, Type 7/8 Augs, Type 5 Augs, and Raid BiS) | Filter Missing Spells, Missing Useful Spells, Raid Achievements, Missing Collections, Quests, etc. to one character; on **Type 5 Augs** / **Type 7/8 Augs** / **Raid BiS**, filter to one persona |
| **Rune type** | Toolbar (Missing Spells) | All / Minor / Lesser / Median / Greater / Glowing |
| **Expansion** dropdown | Toolbar (table tabs) | Filter **Missing Spells**, **Missing Useful Spells**, and achievement tables by expansion (full name plus year; defaults to the **current expansion** on first open for achievements); on **Missing Runes** and **Rune Inventory**, filter to one expansion / rune family |
| **Zone** | Toolbar (Quests) | Filter Mercenary/Partisan rows to one zone (options follow the current Expansion filter) |
| **Event** | Toolbar (Raid Achievements) | Filter raid cards to one event (e.g. Echo of Hate). Options follow the current Expansion filter |
| **Sort** | Toolbar (Missing Runes) | Reorder character columns: roster order, name, class, or most missing (uses the Expansion filter when one is selected) |
| **Column headers** | Table | Click to sort |
| **Missing Item** | Missing Collections | Hover the header for a copy reminder; click an item name to copy it |

Gear-set and tier colors match the Excel theme. Item names, Gear T-Level codes, and Missing Spells / Missing Useful Spells names link to EQ Resource; hover a T-code for the item name.

---

## Tips

- **Whole raid in one folder** — use **EQ Folder** after everyone copies output files into the same directory.  
- **Spell files in SpellData** — keeps the inventory folder organized; the app finds them automatically.  
- **Achievement files in AchievementData** — same pattern for `/outputfile achievements` files.  
- **Status bar** — shows how many inventory, MissingSpells, and achievement files are loaded.  
- **Up** / **Down** / **Remove** / **Clear** — under Output folder on the right; fix the roster before regenerating.  
- **Warnings** — if a character has inventory but no spell file, you’ll get a message after export; the workbook still builds.
- **Gear tier colors** — customize the five report bucket colors; they persist across launches (saved in AppData). **Reset to default** undoes that.
- **Help** (top right) — gear tier colors legend (your current palette), **Check for Updates** (same GitHub Release check as startup), and **About EQGM** (shows the app version).

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| “Add at least one *-Inventory.txt” | Spell files alone are not enough — add inventory files. |
| GUI window is blank or fails to start | Install the [WebView2 runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Evergreen bootstrapper). |
| Spell tabs empty | Confirm spell file names match `Name_server-CLASS-MissingSpells.txt` and character names match inventory files. |
| Achievement tabs empty | Confirm achievement file names match `Name_server-Achievements.txt` and character/server match inventory files. |
| Include chips are grayed out | No inventory files in the roster yet. |
| “Permission denied” / save failed | Close the workbook in Excel and try again. |
| Wrong characters in columns | Each inventory file should be one character; check filenames. |
| Type 7/8 Augs sheets missing or empty | Leave the **Type 7/8 Augs** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Type 7/8 note says to move an aug, but **Upgrade to** is blank | Use **1.30.3** or newer and regenerate the report. Older builds marked that donor hole as BiS. |
| Type 5 Augs sheet missing or empty | Leave the **Type 5 Augs** chip on; sockets and aug stats use the same `%LOCALAPPDATA%\EQGM\` cache as Type 7/8 (first run may need network). |
| Type 18/19 Augs sheet missing or empty | Leave the **Type 18/19 Augs** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Raid BiS sheet missing or slots look empty | Leave the **Raid BiS** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| HTML looks outdated after an update | Regenerate the report. |
| Warning: “Failed to remove temporary directory …\_MEI…” | Harmless packaging cleanup from the single-file `.exe`. Windows (or antivirus) sometimes keeps a handle open after exit, so PyInstaller cannot delete its extract folder. Click **OK** and keep working. You can delete leftover `_MEI*` folders under `%TEMP%` when EQGM is closed. It is unrelated to reading your EverQuest folder. |
