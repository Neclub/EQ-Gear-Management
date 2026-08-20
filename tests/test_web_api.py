"""Tests for web API helpers (no pywebview window)."""

from pathlib import Path

from inventory_parser.web_api import WebApi, _choice_summary, _gui_error_payload, _public_error_message


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


def test_generate_report_writes_html(tmp_path: Path) -> None:
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
            "includeSlot2": False,
            "outputFormat": "both",
        }
    )
    assert result["ok"] is True
    assert result["xlsx"]
    assert Path(result["xlsx"]).is_file()
    assert result["html"]
    assert Path(result["html"]).is_file()


def test_generate_report_excel_only(tmp_path: Path) -> None:
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
            "includeSlot2": False,
            "outputFormat": "excel",
        }
    )
    assert result["ok"] is True
    assert result["xlsx"]
    assert Path(result["xlsx"]).is_file()
    assert result["html"] is None
    assert not (tmp_path / "solo.html").exists()


def test_generate_report_html_only(tmp_path: Path) -> None:
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
            "includeSlot2": False,
            "outputFormat": "html",
        }
    )
    assert result["ok"] is True
    assert result["xlsx"] is None
    assert not out.exists()
    assert result["html"]
    assert Path(result["html"]).is_file()


def test_generate_report_multi_character_writes_html(tmp_path: Path) -> None:
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
            "includeSlot2": False,
            "outputFormat": "both",
        }
    )
    assert result["ok"] is True
    assert result["html"]
    assert Path(result["html"]).is_file()


def test_get_and_set_output_format(tmp_path, monkeypatch) -> None:
    from inventory_parser import character_column_order as module

    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(module, "settings_path", lambda: settings_file)
    api = WebApi()
    assert api.get_gui_prefs()["outputFormat"] == "both"
    assert api.get_gui_prefs()["lastEqFolder"] is None
    assert api.set_output_format("excel")["outputFormat"] == "excel"
    assert api.get_gui_prefs()["outputFormat"] == "excel"
    assert api.set_output_format("nope")["outputFormat"] == "both"


def test_pick_folder_remembers_last_directory(tmp_path, monkeypatch) -> None:
    from inventory_parser import character_column_order as module
    from inventory_parser.web_api import webview

    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(module, "settings_path", lambda: settings_file)
    first = tmp_path / "logs_a"
    second = tmp_path / "logs_b"
    first.mkdir()
    second.mkdir()

    class FakeWindow:
        def __init__(self) -> None:
            self.calls: list[dict] = []

        def create_file_dialog(self, dialog_type, **kwargs):
            self.calls.append({"type": dialog_type, **kwargs})
            if len(self.calls) == 1:
                return [str(first)]
            return [str(second)]

    window = FakeWindow()
    api = WebApi()
    api.bind_window(window)

    assert api.pick_folder() == str(first.resolve())
    assert window.calls[0]["type"] == webview.FileDialog.FOLDER
    assert "directory" not in window.calls[0]
    assert api.get_gui_prefs()["lastEqFolder"] == str(first.resolve())

    assert api.pick_folder() == str(second.resolve())
    assert window.calls[1]["directory"] == str(first.resolve())
    assert api.get_gui_prefs()["lastEqFolder"] == str(second.resolve())


def test_open_html_report_missing_file() -> None:
    api = WebApi()
    result = api.open_html_report("nonexistent_report.html")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_fit_window_without_window() -> None:
    api = WebApi()
    assert api.fit_window(900, 700) == {"ok": False}


def test_fit_window_skips_when_maximized() -> None:
    class FakeWindow:
        maximized = True
        fullscreen = False

        def resize(self, width: int, height: int) -> None:
            raise AssertionError("maximized window should not resize")

    api = WebApi()
    api.bind_window(FakeWindow())
    assert api.fit_window(1200, 900) == {"ok": True, "skipped": True}


def test_fit_window_moves_above_work_area_bottom(monkeypatch) -> None:
    from inventory_parser import web_api as module

    class FakeWindow:
        maximized = False
        fullscreen = False
        x = 100
        y = 800
        native = None
        moved = None
        sized = None

        def resize(self, width: int, height: int) -> None:
            self.sized = (width, height)

        def move(self, x: int, y: int) -> None:
            self.moved = (x, y)

    monkeypatch.setattr(module, "_work_area_for_hwnd", lambda hwnd: (0, 0, 1920, 1040))
    fake = FakeWindow()
    api = WebApi()
    api.bind_window(fake)
    result = api.fit_window(900, 700)
    assert result["ok"] is True
    assert fake.sized == (900, 700)
    assert fake.moved == (100, 340)
    assert result["y"] == 340


def test_start_window_drag_without_window() -> None:
    api = WebApi()
    assert api.start_window_drag() == {"ok": False}


def test_public_error_redacts_home_path() -> None:
    home = str(Path.home())
    message = _public_error_message(FileNotFoundError(f"{home}\\Downloads\\report.xlsx"))
    assert home not in message
    assert message.startswith("~")
    payload = _gui_error_payload(RuntimeError(f"failed in {home}"))
    assert payload == {"ok": False, "error": "failed in ~"}
    assert "traceback" not in payload
