# In-Game Output Files

On each character, run these chat commands in EverQuest:

| Command | Creates |
|---------|---------|
| `/outputfile inventory` | Inventory file (`*-Inventory.txt`) |
| `/outputfile inventory CHR_Server-CLASS-Inventory.txt` | Optional — persona inventory (`*-CLASS-Inventory.txt`). A hotkey per persona is suggested. |
| `/outputfile missingspells` | Missing spells file (`*-MissingSpells.txt`) |
| `/outputfile achievements` | Achievement file (`*-Achievements.txt`) |

EQ writes the files to the root of your **EverQuest** folder (not `Logs`). Point **EQ Folder** at that folder — each character needs their own inventory file; add spell and/or achievement files when you want those tabs.

---

## Inventory files (required)

At least one file named like:

`CharacterName_server-Inventory.txt`

Example: `CharN_bristle-Inventory.txt`

Tab-separated text from `/outputfile inventory`. The file reflects **equipped items for the active persona only**.

You can also write a class-tagged inventory directly (same pattern as MissingSpells) with `/outputfile inventory CHR_Server-CLASS-Inventory.txt`:

`CharacterName_server-CLASS-Inventory.txt`

Example: `CharN_bristle-PAL-Inventory.txt`

### Alternate personas

EQ’s Alternate Persona system lets one character swap class while sharing bank, bags, and other data. Each persona’s worn gear can be tracked as its own Team Gear column when you have a separate inventory file per class. Achievements and collections are shared across personas — they appear once per character, not once per class column.

**Class-tagged inventories (preferred for personas):** put `CharacterName_server-CLASS-Inventory.txt` files in the same folder with matching `CharacterName_server-CLASS-MissingSpells.txt` files. Each class file becomes its own column (e.g. `CharN ( PAL )`, `CharN ( SHD )`). If any class-tagged inventory exists for a character, the generic `CharacterName_server-Inventory.txt` for that character is ignored.

**Same folder with only a generic inventory:** one inventory plus MissingSpells file(s). Add the spell file for the active persona to get a Team Gear column labeled with that class. If you add only the inventory and multiple spell files are auto-discovered, Team Gear is skipped (spell tabs only).

**Subfolders (also supported):** each persona’s folder contains the standard inventory name plus its spell file — e.g. `PAL/CharN_bristle-Inventory.txt` + `PAL/CharN_bristle-PAL-MissingSpells.txt`. Same-folder class-tagged names are preferred when available.

**How class is determined:** reports label each column from the **worn Chest (breastplate)** in that inventory file (looked up on raidloot, then EQ Resource, and cached). MissingSpells and class-tagged inventory filenames still pair personas and are used when the chest is empty or the lookup cannot name a class.

---

## Missing Spells files (optional)

Files named like:

`CharacterName_server-CLASS-MissingSpells.txt`

Example: `Healub_bristle-CLR-MissingSpells.txt`

From `/outputfile missingspells`. One line per spell: `level` + tab + `spell name`. Rank 1 spells that were never purchased are listed by name only (EverQuest does not write `Rk. I`). Rank is only `Rk. II` or `Rk. III`; roman numerals in the spell name (for example Yaulp XIX) are the spell line, not rank. EQGM treats never-purchased rank 1 and missing Rk. II as missing Rk. III. The **CLASS** in the MissingSpells filename identifies the persona for pairing files; class-tagged inventory filenames use the same abbreviation. Column labels and useful-spell matching prefer the worn Chest class when it can be resolved.

You can put spell files:

- In the **same folder** as the inventory files, or
- In a subfolder named **`SpellData`** next to those files

You still need at least one inventory file to build the workbook.

---

## Achievement files (optional)

Files named like:

`CharacterName_server-Achievements.txt`

Example: `Shamlub_xegony-Achievements.txt`

From `/outputfile achievements`. Tab-separated text with section headers (`Expansion: Collections`, `General: Advancement`, etc.) and status lines (`C` completed, `I` incomplete).

You can put achievement files:

- In the **same folder** as the inventory files, or
- In a subfolder named **`AchievementData`** next to those files

Achievement files are named by character only (no class segment); with multiple persona inventories, those tabs still list each character once.

See also: [[Getting Started]], [[Quests and Achievements]].
