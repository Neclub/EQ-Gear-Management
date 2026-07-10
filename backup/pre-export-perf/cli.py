from __future__ import annotations



import argparse

import sys

from pathlib import Path



from inventory_parser import __version__

from inventory_parser.team_report import (

    discover_input_files,

)

from inventory_parser.excel_export import write_team_workbook

from inventory_parser.export_bundle import build_export_bundle, release_export_memory

from inventory_parser.html_export import write_team_html

from inventory_parser.output_paths import html_path_for_workbook

from inventory_parser.slots import SlotFilter





def generate_workbook(

    input_paths: list[Path],

    output_path: Path,

    *,

    slot_filter: SlotFilter = "all",

    include_spells: bool = True,

    include_achievements: bool = True,

    also_html: bool = False,

    character_column_order: list[str] | None = None,

) -> tuple[Path, list[str], Path | None]:

    """Parse inventories and write the team inventory Excel file."""

    bundle = build_export_bundle(

        input_paths,

        slot_filter=slot_filter,

        include_spells=include_spells,

        include_achievements=include_achievements,

        character_column_order=character_column_order,

    )

    warnings = list(bundle.warnings)

    try:

        saved = write_team_workbook(

            bundle.team,

            output_path,

            slot_filter=bundle.slot_filter,

            spell_report=bundle.spell_report,

            rune_inventory_report=bundle.rune_inventory_report,

            achievement_report=bundle.achievement_report,

        )

        html_saved = None

        if also_html:

            html_saved = write_team_html(bundle, html_path_for_workbook(saved))

        return saved, warnings, html_saved

    finally:

        del bundle

        release_export_memory()





def main(argv: list[str] | None = None) -> int:

    p = argparse.ArgumentParser(

        description="Build team inventory Excel from EverQuest *-Inventory.txt dumps.",

        prog="inventory-parser",

    )

    p.add_argument(

        "--version",

        action="version",

        version=f"%(prog)s {__version__}",

    )

    p.add_argument(

        "inventories",

        nargs="*",

        type=Path,

        help="Inventory dump file(s). If omitted, use --folder.",

    )

    p.add_argument(

        "--folder",

        type=Path,

        help="Folder containing *-Inventory.txt files (used when no files are listed)",

    )

    p.add_argument(

        "-o",

        "--output",

        type=Path,

        required=True,

        help="Output .xlsx path",

    )

    p.add_argument(

        "--slots",

        choices=("all", "visible", "non_visible"),

        default="all",

        help="Which slots to include (default: all, sorted visible then non-visible)",

    )

    p.add_argument(

        "--no-spells",

        action="store_true",

        help="Skip Missing Runes and Missing Spells tabs even if *-MissingSpells.txt files are found",

    )

    p.add_argument(

        "--no-achievements",

        action="store_true",

        help="Skip Missing Collections and Achievement Summary tabs even if *-Achievements.txt files are found",

    )

    p.add_argument(

        "--also-html",

        action="store_true",

        help="Also write an interactive HTML report next to the Excel file (same name, .html)",

    )

    args = p.parse_args(argv)



    paths: list[Path] = list(args.inventories)

    if args.folder:

        paths.extend(discover_input_files(args.folder))

    paths = [p.resolve() for p in paths]

    if not paths:

        print("Provide inventory file(s) or --folder.", file=sys.stderr)

        return 2



    try:

        saved, warnings, html_saved = generate_workbook(

            paths,

            args.output,

            slot_filter=args.slots,

            include_spells=not args.no_spells,

            include_achievements=not args.no_achievements,

            also_html=args.also_html,

        )

    except ValueError as exc:

        print(exc, file=sys.stderr)

        return 1



    for w in warnings:

        print(w, file=sys.stderr)

    print(f"inventory-parser {__version__} — saved: {saved}", file=sys.stderr)

    if html_saved is not None:

        print(f"inventory-parser {__version__} — saved: {html_saved}", file=sys.stderr)

    return 0





if __name__ == "__main__":

    raise SystemExit(main())


