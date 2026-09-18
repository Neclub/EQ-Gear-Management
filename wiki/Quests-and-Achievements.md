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

## Hunters

Incomplete **zone hunter** lines from each expansion’s **Hunter** or **Hunts** section. Fully complete zones are omitted. If a zone is still in progress, every NPC target is listed so you can see what is left.

**Excel columns:** Character · Expansion · Hunter · Zone · Target · Status (`Done` / `Missing`)

**HTML:** each zone is a card headed by the **Hunter of** line (e.g. `Hunter of Arcstone, Shattered Isles`). Child rows are the NPC names. Incomplete kills show an empty box; finished kills show **X**.

Rank metas (Novice / Adept / Veteran / Expert / Master) and region grouping parents (e.g. `Hunter of Faydwer`) are omitted — only zone kill lists appear.

Expansions show release year and rows are sorted **newest to oldest**. In HTML, **Character**, **Expansion**, and **Zone** dropdowns narrow the list (expansion defaults to the current expansion; Zone options follow the selected expansion).

---

## Slayer

**Megadeath** progress from **Slayer: General** in each character’s achievement dump. The three required metas are listed: A Force of Nature, Highly Decorated, and Progressive. Skill / Special / Conquest kill-count lines are not listed. Fully complete Megadeath still appears so finished characters stay visible.

**Excel columns:** Character · Achievement · Objective · Status (`Done` / `Missing`)

**HTML:** one card per character headed by **Megadeath**. Incomplete steps show an empty box; finished steps show **X**. **Character** dropdown narrows the list (no expansion filter).

---

## Tradeskills

Skill levels inferred from completed **`Skill (N)`** achievements under **Tradeskill** in each character’s dump (e.g. `Baking (150)`, `Smithing (100)`). The value shown is the highest completed milestone — not the live skill window — so a character at 175 baking still shows **150**.

**Always listed:** Baking · Blacksmithing (dump name `Smithing`) · Brewing · Fishing · Fletching · Jewelcrafting · Pottery · Tailoring · Research (Research lives under **Tradeskill: Special** but every class can have it).

**Special** (only if that skill appears in the dump): Alchemy · Tinkering · Poisonmaking. Omitted entirely when the character has no achievements for that skill.

**Excel columns:** Character · Baking · Blacksmithing · Brewing · Fishing · Fletching · Jewelcrafting · Pottery · Tailoring · Research · Alchemy · Tinkering · Poisonmaking. Special cells are blank when that skill is not in the dump; otherwise the numeric level (including `0`).

**HTML:** one card per character with skill name and level. A **Special** subhead appears only when that character has special skills. An **Achievements** chip next to the anvil reminds you the numbers are from completed achievements, not live skill (hover for the full tip). **Character** dropdown and search narrow the list (no expansion filter).

---

## Heroic AA

Ranks of **Hero's Fortitude**, **Hero's Resolution**, and **Hero's Vitality** from completing the wiki list of Hero's Special AAs. Each `/outputfile achievements` dump is compared to that list (in-game names, with wiki aliases). Incomplete entries stay listed so you can see what is left. Not every achievement awards all three ranks — HTML only shows F / R / V chips for ranks that achievement grants (lit when Completed, muted when still Incomplete); Excel leaves Fortitude / Resolution / Vitality blank when that rank is not awarded. Achievement names link to [EQ Resource](https://achievements.eqresource.com/) when the catalog includes an id.

**Excel columns:** Character · Expansion · Achievement · Fortitude · Resolution · Vitality · Status (`Completed` / `Incomplete`)

**HTML:** a totals banner (Fortitude / Resolution / Vitality / achievements completed) and an expansion-grouped list with F / R / V chips. Hover a total for the AA’s effect; hover **F** / **R** / **V** for Fortitude, Resolution, and Vitality. Click an achievement name to open EQ Resource. **Character**, **Expansion**, and **Achievements** (All / Completed / Incomplete) filters apply. Credit links to Fanra’s wiki.

---

## Achievement Summary

Top-level achievement counts per section (expansion or category): completed, incomplete, total, and completion percentage.

See also: [[HTML Report]], [[Troubleshooting]].
