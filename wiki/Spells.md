# Spells

Spell and rune tabs use **MissingSpells** files. **Rune Inventory** also reads bags from inventory files. Spell names link to [EQ Resource spells](https://spells.eqresource.com).

Enable or disable with the **Spells** chip on the [[Setup Screen]].

---

## Missing Runes

How many Minor / Lesser / Median / Greater / Glowing runes each character still needs, grouped by the **spell expansion** each missing Rk. III spell comes from:

| Expansion | Rk. III rune item |
|-----------|-------------------|
| Laurion's Song (LS) | `{Tier} Emblem of the Forge` |
| The Outer Brood (ToB) | `Energized {Tier} Engram` |
| Shattering of Ro (SoR) | `{Tier} Mirrorshard of Relic` |

`{Tier}` = Minor, Lesser, Median, Greater, or Glowing (one per spell level). Each expansion gets its own matrix on the **Missing Runes** sheet and HTML tab — a character missing both LS and ToB spells at level 123 shows separate LS and ToB rune counts. In HTML, **Sort** reorders character columns (roster, name, class, or most missing); **Expansion** narrows to one expansion.

---

## Missing Spells

Every missing **Rk. III** spell at levels 121–130, including missing **Rk. II** and spells that were **never purchased**, displayed as Rk. III. Columns: character, level, rune tier, **expansion**, and spell name. Never-purchased spells show a **Not Purchased** chip in HTML, or the same label after the name in Excel. Spell names link to [EQ Resource](https://spells.eqresource.com) (direct spell page when the catalog has an id; otherwise a name search).

**Columns:** Character · Level · Rune · Expansion · Spell

Expansion is looked up from a bundled EQ Resource catalog for levels **121–130**. The same level band can mix expansions — e.g. a level 123 wizard may need Laurion's Song runes for some spells and The Outer Brood runes for others. Use Excel or HTML filters on **Expansion** or **Rune type** to narrow the list.

Missing Rk. II lines and never-purchased rank 1 spells at rune-relevant levels count toward **Missing Runes** the same as Rk. III. Spells not in the catalog (gates, Mastery lines, etc.) may list with a blank expansion and are not counted on **Missing Runes**.

Older level bands (111–120) are in config but not shown until enabled in `spell_rune_bands.json`.

---

## Missing Useful Spells

Useful spells from [Raccoo’s curated list](https://docs.google.com/spreadsheets/d/1ZqUFZ-WTZvfcBfwu5g6GGEQroEwNLSfK1LMOdMHVHcA/htmlview) that still appear in each character’s MissingSpells file — **all levels**, not just 121–130.

**Columns:** Character · Level · Expansion · Spell · Highest RK · Comments

Matching is by class (worn Chest when known, otherwise the MissingSpells filename) against the bundled useful-spell catalog. Spell names link to EQ Resource the same way as **Missing Spells**. Use Excel auto-filter or the HTML **Character** / **Expansion** dropdowns to focus on one persona. The sheet includes a credit link: **Based on "SOR - Raccoo's list of useful spells"**.

---

## Rune Inventory

On-hand raid spell rune items in **General**, **Bank**, and **Shared Bank** — no MissingSpells file required.

Four sections (NoS, LS, ToB, SoR), each with a tier × character matrix. Cells show the stack count when > 0; otherwise blank. Inert and Covariant Engrams are not counted (ToB uses **Energized** engrams only).

| Family | Item pattern |
|--------|----------------|
| NoS | `{Tier} Symbol of Shar Vahl` |
| LS | `{Tier} Emblem of the Forge` |
| ToB | `Energized {Tier} Engram` |
| SoR | `{Tier} Mirrorshard of Relic` |

See also: [[In-Game Output Files]], [[HTML Report]].
