# Augs

Aug sections are optional and **on by default** when inventories are loaded. Toggle them with chips on the [[Setup Screen]]. Type 7/8, Type 5, Type 18/19, and Raid BiS catalogs reuse disk cache under `%LOCALAPPDATA%\EQGM\` after the first fetch.

---

## Type 7/8 Augs

Type 7/8 (usually inventory Slot2) recommendations vs an EQ Resource catalog (raidloot fallback). Only augs that **fit type 7/8 holes** are recommended (type 5 and similar are excluded). Artisan's Prize is treated as owned when it appears in the inventory file. If **Velium Empowered Gem of Freezing** is equipped, it is kept and assigned to the legal slot with the best weighted trade-off against other BiS augs. Scoring uses class weights: tanks AC then HDex; melee HDex; priests (CLR, SHM) HWis; INT casters Spell Damage. **DRU** ranks Spell Damage first (weight 9) with HWis as a secondary (weight 1). Override for one character under **Advanced weights**. Excel adds **Stat Summary**, **Augs**, **Need to Farm**, **Ranked Augs**, and **Aug Legend**. HTML adds a **Type 7/8 Augs** section with the same cards. Needs a network fetch the first time; later runs reuse the catalog cache. Uncheck the chip to skip this entirely.

**Slot recommendations** compare **Current** to **Upgrade to**. Hover the **?** for a reminder that these are suggestions — some classes already sit at a stat cap. **BiS** leaves Upgrade to blank — that hole already has the suggested aug. If a note says to move an aug to another slot (Charm, Range, Feet, and similar priority holes can claim a piece sitting elsewhere), Upgrade to lists what should replace it in the hole being vacated. The destination row shows a **Move from** badge.

When a recommended aug still needs a Focus of Fortitude (Unraveling, Otherworldly, Gallant, or Focus of Uprising) or Ensanguined ore, HTML shows a **Need** or **Have** chip that links to EQ Resource. **Slot recommendations** and **Need to farm** both use those chips. Regenerating after an app update is required for older HTML files to pick this up.

When the Type 7/8 chip is on, optional **Include Anniversary augs** appears, plus **Advanced weights** for a single-character roster.

---

## Type 5 Augs

Display-only list of what is in each type 5 hole (often inventory Slot2 on current gear, but the dump SlotN comes from the parent item’s socket map). Empty holes show as **Empty**. Columns include **Expansion** (from EQ Resource) and heroic stats (HStr through HCha) when an aug is equipped. Vanquisher raid-achievement augs (from Terror of Luclin onward) show a short Expansion label instead — e.g. `Vanq ToL`, `Vanq NoS`, `Vanq LS`, `Vanq ToB`, `Vanq SoR` — linked to the achievement page (hover shows the full Vanquisher title). No BiS or farm suggestions — preference only. Excel adds a **Type 5 Augs** sheet; HTML adds a **Type 5 Augs** section with **one card per character** (same gold nameplate and class badge as Raid BiS), a **Character** filter (All or one character), clickable column headers to sort, and a link to the [EQ Resource Type 5 list](https://items.eqresource.com/itemsearch.php?searchid=481762). Uncheck the chip to skip.

---

## Type 18/19 Augs

*(work in progress)*

Per-class **Primary** and **Optional** suggestions from the Zarax Type 18/19 cheat sheet, resolved against the EQ Resource catalog (stats / item links). This feature is still being refined. Defense-family picks are moved to Optional. The top two unused **Fortification** augs from the catalog are appended to Optional (greatest→least). Unused **Enhancement** augs are listed under **Filler** (greatest→least). If a better aug exists in the same category, type, and expansion series, that pick is used. **Anniversary** augs (Jubilation / Enduring Harmony) are marked on the item name (HTML chip / Excel highlight) and always get a non-anniversary **Alternative**. Selenelion augs are crafts, not anniversary. Non-anniversary augs show a craft (anvil) icon in HTML; click copies the name for pasting into EQ Traders or chat. Caster classes show **Mana** / **Spell Damage** instead of AC / HP.

**HTML:** **Suggestions** view with a toolbar **Character** select (sets class; **Owned** when that character has the aug, with a location chip when it is currently equipped). An **Alternative** that is owned and equipped gets Owned plus a location chip; otherwise it gets the craft anvil. **Full catalog** view keeps lore/category filters.

**Excel:** **Type 18-19 Augs** (suggestions per character; columns auto-sized) and **Type 18-19 Catalog**. Dual-slot `18, 19` → **18/19**; `19` only → **19**. Needs a network fetch the first time; later runs reuse `%LOCALAPPDATA%\EQGM\` catalog cache. Toggle with the Include chip.

See also: [[Setup Screen]], [[HTML Report]], [[Troubleshooting]].
