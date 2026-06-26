# Expansion Update Plan

Maintainer documentation for adding a new EverQuest expansion to Inventory Parser.

## Contents

| Document | Purpose |
|----------|---------|
| [December-2026-Expansion-Update.md](December-2026-Expansion-Update.md) | Full phased checklist, EQ Resource link prompts, code touch list, and validation steps |

## When to use

Start **Phase 1** when the expansion is announced (target: **December 2026**). Run scrapers and code updates once EQ Resource pages and in-game item names are live.

## Quick workflow

1. Fill in the Phase 1 checklist in the main plan doc.
2. Run scrapers (`build_vendor_json.py`, `scrape_spell_expansions.py`).
3. Update gear/rune/achievement config files.
4. Run `py -3 -m pytest` and smoke-test exports.

See the main plan for copy-paste prompts and the master checklist.
