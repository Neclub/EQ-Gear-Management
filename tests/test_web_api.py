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


def test_generate_report_single_character_omits_viewer_payload(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    inv = root / "Examples" / "Deflub_bristle-Inventory.txt"
    out = tmp_path / "solo.xlsx"
    api = WebApi()
    result = api._generate_report_sync(
        {
            "paths": [str(inv)],
            "outputPath": str(out),
            "slotFilter": "all",
            "includeSpells": False,
            "includeAchievements": False,
            "alsoHtml": True,
        }
    )
    assert result["ok"] is True
    assert result["html"]
    assert result["reportPayload"] is None


def test_generate_report_multi_character_includes_viewer_payload(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "Examples"
    paths = [
        str(examples / "Deflub_bristle-Inventory.txt"),
        str(examples / "Healub_bristle-Inventory.txt"),
    ]
    out = tmp_path / "team.xlsx"
    api = WebApi()
    result = api._generate_report_sync(
        {
            "paths": paths,
            "outputPath": str(out),
            "slotFilter": "all",
            "includeSpells": False,
            "includeAchievements": False,
            "alsoHtml": True,
        }
    )
    assert result["ok"] is True
    assert result["reportPayload"] is not None
    assert result["reportPayload"]["meta"]["characterCount"] == 2
