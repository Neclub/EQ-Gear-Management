# Expansion Update Plan

Maintainer documentation for adding a new EverQuest expansion to EQ Gear Management.

## Contents

| Document | Purpose |
|----------|---------|
| [Scrapes-Needed.md](Scrapes-Needed.md) | Concrete list of EQ Resource scrapes (and useful-spells convert) for the next expansion |
| [December-2026-Expansion-Update.md](December-2026-Expansion-Update.md) | Full phased checklist, EQ Resource link prompts, code touch list, and validation steps |

## When to use

Start **Phase 1** when the expansion is announced (target: **December 2026**). Run scrapers and code updates once EQ Resource pages and in-game item names are live. Use [Scrapes-Needed.md](Scrapes-Needed.md) as the launch-day scrape checklist.

## Quick workflow

1. Fill in the Phase 1 checklist in the main plan doc (and the scrape URL records in Scrapes-Needed).
2. Run scrapers (`build_vendor_json.py`, `scrape_spell_expansions.py`) — see Scrapes-Needed for exact commands.
3. Update gear/rune/achievement config files.
4. Run `py -3 -m pytest` and smoke-test exports.

See the main plan for copy-paste prompts and the master checklist.
