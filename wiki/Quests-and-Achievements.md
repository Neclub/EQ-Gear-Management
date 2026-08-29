# Quests and Achievements

These tabs use **`/outputfile achievements`** files. Enable or disable with the **Achievements** chip on the [[Setup Screen]]. File naming and folders: [[In-Game Output Files]].

Personas of the same character share one achievement file — rows are once per character, not per class column.

---

## Missing Collections

Every incomplete collection item under a **Collections** section: character, expansion/category, zone (from a `(Zone)` suffix on the collection name, or from a `{Zone} Scavenger` grouping), collection name, missing item, progress, which team member has the item in inventory (**Char Has**), and total needed. Personas of the same character share one inventory for collections — rows and **Char Has** names are once per character, not per class. **Stalking Fear** (Rain of Fear) is omitted from this list. In HTML, hover **Missing Item** for a reminder that clicking a name copies it; a small balloon confirms it was added to the clipboard.

---

## Quests

Unfinished **Mercenary** and **Partisan** zone quest lines from each expansion’s **Quests** section. Fully complete lines are omitted. If a line is still in progress, every child quest is listed so you can see what is left in that zone.

**Excel columns:** Character · Expansion · Zone · Type · Quest · Status (`Done` / `Missing`)

**HTML:** each Mercenary/Partisan line is a card with the achievement title as the header (e.g. `Partisan of Arcstone, Shattered Isles`) and the child quests underneath as a checklist. Incomplete steps show an empty box; finished steps show **X**.

Expansions show release year (e.g. `Shattering of Ro (2025)`) and rows are sorted **newest to oldest**. In HTML, **Character**, **Expansion**, and **Zone** dropdowns narrow the list (expansion defaults to the current expansion).

---

## Raid Achievements

Incomplete **raid** lines from each expansion’s **Raids** section. Fully complete lines are omitted. If a line is still in progress, every child objective is listed so you can see what is left.

**Excel columns:** Character · Expansion · Raid · Event · Objective · Status (`Done` / `Missing`)

**HTML:** each raid is a card headed by the **Conqueror** line (e.g. `Conqueror of Labyrinth of Spite: Echo of Hate`). Child rows are the event achievements after the colon (Enraged, Give in to Greed, Unfocused, What It Wants). Incomplete steps show an empty box; finished steps show **X**.

Expansions show release year and rows are sorted **newest to oldest**. In HTML, **Character**, **Expansion**, and **Event** dropdowns narrow the list (expansion defaults to the current expansion; Event options follow the selected expansion).

---

## Heroic AA

Ranks of **Hero's Fortitude**, **Hero's Resolution**, and **Hero's Vitality** from completing the wiki list of Hero's Special AAs. Each `/outputfile achievements` dump is compared to that list (in-game names, with wiki aliases). Incomplete entries stay listed so you can see what is left. Not every achievement awards all three ranks — HTML only shows F / R / V chips for ranks that achievement grants (lit when Completed, muted when still Incomplete); Excel leaves Fortitude / Resolution / Vitality blank when that rank is not awarded. Achievement names link to [EQ Resource](https://achievements.eqresource.com/) when the catalog includes an id.

**Excel columns:** Character · Expansion · Achievement · Fortitude · Resolution · Vitality · Status (`Completed` / `Incomplete`)

**HTML:** a totals banner (Fortitude / Resolution / Vitality / achievements completed) and an expansion-grouped list with F / R / V chips. Hover a total for the AA’s effect; hover **F** / **R** / **V** for Fortitude, Resolution, and Vitality. Click an achievement name to open EQ Resource. **Character**, **Expansion**, and **Achievements** (All / Completed / Incomplete) filters apply. Credit links to Fanra’s wiki.

---

## Achievement Summary

Top-level achievement counts per section (expansion or category): completed, incomplete, total, and completion percentage.

See also: [[HTML Report]], [[Troubleshooting]].
