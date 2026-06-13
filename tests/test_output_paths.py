from pathlib import Path

from inventory_parser.team_report import build_team_report
from inventory_parser.eq_servers import server_display_name, server_slug_from_eqlog_filename
from inventory_parser.output_paths import (
    team_inventory_filename,
    default_export_prefix_from_input_paths,
    default_export_prefix_from_report,
    is_auto_team_inventory_path,
    server_slug_from_input_paths,
    server_slug_from_report,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "Examples"
SPELL_DATA = EXAMPLES / "SpellData"
EQLOG = Path(__file__).resolve().parents[2] / "Example" / "Roots" / "eqlog_Neclub_bristle.txt"


def test_server_display_name_bristle() -> None:
    assert server_display_name("bristle") == "Bristlebane"


def test_server_display_name_unknown_slug() -> None:
    assert server_display_name("customtlp") == "Customtlp"


def test_team_inventory_filename_with_prefix() -> None:
    assert team_inventory_filename("Bristlebane") == "Bristlebane_Team Inventory.xlsx"
    assert team_inventory_filename("Deflub") == "Deflub_Team Inventory.xlsx"
    assert team_inventory_filename() == "Team Inventory.xlsx"


def test_default_export_prefix_single_character() -> None:
    path = EXAMPLES / "Deflub_bristle-Inventory.txt"
    assert default_export_prefix_from_input_paths([path]) == "Deflub"


def test_default_export_prefix_multiple_characters() -> None:
    paths = sorted(EXAMPLES.glob("*-Inventory.txt"))
    assert default_export_prefix_from_input_paths(paths) == "Bristlebane"


def test_default_export_prefix_from_report() -> None:
    report = build_team_report([EXAMPLES / "Deflub_bristle-Inventory.txt"])
    assert default_export_prefix_from_report(report) == "Deflub"
    report = build_team_report(sorted(EXAMPLES.glob("*-Inventory.txt")))
    assert default_export_prefix_from_report(report) == "Bristlebane"


def test_server_slug_from_inventory_examples() -> None:
    paths = sorted(EXAMPLES.glob("*-Inventory.txt"))
    assert server_slug_from_input_paths(paths) == "bristle"


def test_server_slug_from_missingspells_only() -> None:
    path = SPELL_DATA / "Deflub_bristle-PAL-MissingSpells.txt"
    assert server_slug_from_input_paths([path]) == "bristle"


def test_server_slug_from_eqlog_filename() -> None:
    assert server_slug_from_eqlog_filename("eqlog_Neclub_bristle.txt") == "bristle"
    assert server_slug_from_eqlog_filename("eqlog_Neclub_beta_202511161721.txt") == "beta"


def test_server_slug_from_eqlog_in_same_folder(tmp_path: Path) -> None:
    inv = tmp_path / "Deflub_bristle-Inventory.txt"
    inv.write_text("Location\tName\tID\n", encoding="utf-8")
    (tmp_path / "eqlog_Deflub_bristle.txt").write_text("", encoding="utf-8")
    assert server_slug_from_input_paths([inv]) == "bristle"
    assert server_slug_from_input_paths([tmp_path / "eqlog_Deflub_bristle.txt"]) == "bristle"


def test_server_slug_from_report() -> None:
    report = build_team_report([EXAMPLES / "Deflub_bristle-Inventory.txt"])
    assert server_slug_from_report(report) == "bristle"


def test_is_auto_team_inventory_path() -> None:
    assert is_auto_team_inventory_path("Team Inventory.xlsx")
    assert is_auto_team_inventory_path(r"D:\Downloads\Bristlebane_Team Inventory.xlsx")
    assert is_auto_team_inventory_path(r"D:\Downloads\Deflub_Team Inventory.xlsx")
    assert is_auto_team_inventory_path("Crew Inventory.xlsx")
    assert is_auto_team_inventory_path(r"D:\Downloads\Bristlebane_Crew Inventory.xlsx")
    assert is_auto_team_inventory_path(r"D:\Downloads\Deflub_Crew Inventory.xlsx")
    assert not is_auto_team_inventory_path("MyRaid.xlsx")
