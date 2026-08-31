# Gear

Excel uses a **dark theme** on every sheet. Item names and Gear T-Level codes link to [EQ Resource](https://items.eqresource.com/) when the inventory file includes item IDs; hover a T-code to see the item name.

Sections below come from **inventory files**.

---

## Team Gear

- One **column per character**, one **row per equipped slot**
- Rows are grouped **visible** gear first, then **non-visible**
- **Colors** show tier bucket — same rules as Gear T-Level; see legend on the sheet (rows 26–30), the **Gear tier colors** panel in the app, or **Help** → gear tier colors
- **Evolver** bucket (purple by default) = Evolver (special augment slot, not the “6” in the Slots column)

---

## Gear T-Level

Same layout as Team Gear, but cells show **what tier is equipped** in each slot. Tier codes link to [EQ Resource](https://items.eqresource.com/) when the inventory includes item IDs; hover a cell to see the item name.

| Cell value | Meaning |
|------------|---------|
| *(blank)* | Empty slot |
| `SOR-R2` | Shattering of Ro R2 (Resonant Fracture) |
| `Evolver` | Evolver item (final augment row in the inventory file) |
| `SOR-R1`, `TOB-R2`, `LS-G2`, etc. | Expansion tier code (`SOR`, `TOB`, `LS`, `NoS` + `G` group or `R` raid + tier number) |
| `???` | Equipped but not recognized after name matching and EQ Resource lookup (e.g. pre-LS expansions) |

See the legend on the Gear T-Level sheet for the full code list. Items whose names are not in the bundled patterns are looked up on EQ Resource; if the page lists an expansion and Raid/Group tier that maps to a known code, that T-code is used instead of `???`. Failed lookups are remembered under `%LOCALAPPDATA%\EQGM\` so Generate Report does not re-query the same unknown items every run — see [[Troubleshooting]] if a later EQ Resource page should have filled in a code.

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

---

## Unmade Gear

Craft materials and T1 containers sitting in **General** bags (SoR / ToB). Every recognized unmade raid item is listed so you can see it is still in inventory; Equipped Tier is shown for context and does not hide rows. Rows follow the same character order as Team Gear.

---

## Raid BiS

*(optional; on by default)*

Current-expansion raid T1 and T2 armor and jewelry vs what each character is wearing, scored with the same class/slot weights as Type 7/8 augs. T1 can beat T2. Evolvers are not scored and may still be BiS; they still get a Best in slot pick and show vendor cost, but that slot is skipped when choosing coin purchases. A pulsing magenta gem next to the equipped item marks an Evolver on hover. MAG, BST, and NEC keep a pet-focus ear (`Enhanced Minion` or `Summoner` in the name). Primary, Secondary, Ammo, and Power Source are shown on the paperdoll but not scored. Wrist items are not Lore, so both wrist slots can recommend the same bracer. An item already equipped is not suggested as BiS for a different slot.

**Waist belts** are a personal choice. The HTML report’s **Best in slot** column shows a dropdown of the three best-statted raid belts — one each for **Overdrive Punch**, **Treaded Boon of Potential**, and **Crippling Slicer**. The default selection is the highest class-weighted of those three; picking another belt updates that row’s **Stat changes**, the character total, and the paperdoll. A **?** next to the Waist stat changes explains the three-belt choice on hover. Excel shows the class-weighted default and notes that Waist is a personal choice (use the HTML report to compare).

**Raid coins:** each HTML character card has a coin box on the right, labeled with the current expansion’s raid currency (**Forgotten Ruined Coin** for Shattering of Ro). That value is only used for that character. Best in slot rows show a coin after the recommended item (including Evolver slots); hover it for the raid vendor cost — T2 recommendations use the slot’s vendor **ore** (Fractured lining/clasp/fastener); T1 jewelry that is sold on the vendor shows that item’s cost. Enter how many coins you have: the report marks the best affordable upgrade with a **Best Purchase** bubble. If you can afford more than one, it picks the combination that gains the most weighted stats for the coins you have. Evolver slots are not included in those purchase picks.

**Excel:** a **Raid BiS** sheet with current item, recommended item, tier, vendor cost/item, and stat changes.

**HTML:** an inventory-window paperdoll (green outline = already BiS, gold = upgrade) plus a table of every scored slot. Character names use a gold nameplate with a class badge. Hover **Raid BiS** for scoring notes. A **Character** dropdown filters to one persona (`Name ( CLASS )`). Stat changes list HP, the class’s primary HStat, AC for tanks (WAR/PAL/SHD), Mana except for WAR/ROG/MNK/BER, and Spell Damage for casters.

Needs a network fetch the first time (EQ Resource raid armor/jewelry, raidloot fallback); later runs reuse the `%LOCALAPPDATA%\EQGM\` catalog cache. Item icons are cached at generate time. Uncheck the **Raid BiS** chip to skip.

See also: [[Setup Screen]], [[HTML Report]].
