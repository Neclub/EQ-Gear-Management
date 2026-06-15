"""Tests for web API helpers (no pywebview window)."""

from pathlib import Path

from inventory_parser.web_api import WebApi, _choice_summary


def test_choice_summary_formats_counts() -> None:
    from inventory_parser.team_report import FolderCharacterChoice

    choice = FolderCharacterChoice(
        character="Deflub",
        server="bristle",
        inventory_paths=(Path("a.txt"),),
        spell_paths=(Path("b.txt"), Path("c.txt")),
    )
    summary = _choice_summary(choice)
    assert "1 inventory" in summary
    assert "2 MissingSpells" in summary


def test_build_roster_from_examples() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "Examples"
    inv = next(examples.glob("*-Inventory.txt"))
    api = WebApi()
    roster = api.build_roster([str(inv)])
    assert len(roster) >= 1
    assert roster[0]["displayName"]


def test_split_paths_inventory_only() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "Examples"
    inv = next(examples.glob("*-Inventory.txt"))
    api = WebApi()
    split = api.split_paths([str(inv)])
    assert len(split["inventory"]) == 1
    assert split["spells"] == []


def test_tier_legend_has_rows() -> None:
    api = WebApi()
    data = api.tier_legend()
    assert data["rows"]
    assert data["visibleSlots"]
    assert data["nonVisibleSlots"]
