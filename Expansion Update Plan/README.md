# Expansion Update Plan

Maintainer documentation for adding a new EverQuest expansion to EQ Gear Management.

## Contents

| Document | Purpose |
|----------|---------|
| [Scrapes-Needed.md](Scrapes-Needed.md) | Concrete list of EQ Resource scrapes (and useful-spells convert) for the next expansion |
| [December-2026-Expansion-Update.md](December-2026-Expansion-Update.md) | Fill-in worksheet for Favors of Fortune (FoF): identity, remaining blanks, code touch list, validation |

## When to use

Official name is **Favors of Fortune** (FoF / fof / FOF), EQ Resource’s 33rd expansion. Beta notes from the logged-in [fof.eqresource.com](https://fof.eqresource.com/) pages (2026-10-09) are in the December plan. **Do not change production code, scrapers, or bundled JSON during beta prep.** Run scrapers only when the raid vendor and spell pages list finished items. Use [Scrapes-Needed.md](Scrapes-Needed.md) as the launch-day scrape checklist.

## Quick workflow

1. Fill in the Phase 1 checklist in the main plan doc (and the scrape URL records in Scrapes-Needed).
2. Run scrapers (`build_vendor_json.py`, `scrape_spell_expansions.py`) — see Scrapes-Needed for exact commands.
3. Update gear/rune/achievement config files.
4. Run `py -3 -m pytest` and smoke-test exports.

See the main plan for copy-paste prompts and the master checklist.
