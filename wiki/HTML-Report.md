# HTML Report

When **HTML** or **Both** is selected next to **Generate Report** (default **Both**), the app saves `{prefix}_Team_Inventory.html` next to the Excel path stem (e.g. `Bristlebane_Team_Inventory.html`). HTML-only mode writes that file without creating a workbook. The `.html` opens in your default browser when generation finishes; you can also double-click it later in Chrome, Edge, Firefox, etc.

HTML reports show the EQGM version on the title graphic next to the generated date (for example `9 characters · generated 2026-08-24 · EQGM v1.34.4`), so a shared file tells you which build produced it.

---

## Layout

- **Left sidebar** — EQGM crest, collapsible section groups (**Gear**, **Spells**, **Augs**, **Quests & Achievements**), gold-rail section buttons, Lucide-style icons, then **Character filter** chips (directly under the nav, not at the bottom of the window). Groups start collapsed; click a group heading to expand or collapse its tabs. The browser remembers which groups you leave open.
- **Main area** — rounded title nameplate (e.g. `Bristlebane Team Inventory`, character count, generation date, and EQGM version), toolbar, and the active section’s table
- **Footer** — gear-tier color legend when viewing **Team Gear**

---

## Sections

Same sections as Excel (omitted when empty, same rules as the workbook), grouped in the sidebar:

- **Gear** — Team Gear, Gear T-Level, Raid BiS, Unmade Gear → [[Gear]]
- **Spells** — Missing Spells, Missing Useful Spells, Missing Runes, Rune Inventory → [[Spells]]
- **Augs** — Type 7/8 Augs, Type 5 Augs, Type 18/19 Augs (each when that chip is on) → [[Augs]]
- **Quests & Achievements** — Missing Collections, Quests, Raid Achievements, Heroic AA, Achievement Summary → [[Quests and Achievements]]

---

## Filters & tools

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
| **Achievements** | Toolbar (Heroic AA) | All / Completed / Incomplete |
| **Sort** | Toolbar (Missing Runes) | Reorder character columns: roster order, name, class, or most missing (uses the Expansion filter when one is selected) |
| **Column headers** | Table | Click to sort |
| **Missing Item** | Missing Collections | Hover the header for a copy reminder; click an item name to copy it |

Gear-set and tier colors match the Excel theme. Item names, Gear T-Level codes, and Missing Spells / Missing Useful Spells names link to EQ Resource; hover a T-code for the item name.

If HTML looks outdated after an app update, regenerate the report.
