from pathlib import Path

from inventory_parser.generate_log import (
    LOG_FILENAME,
    format_last_report_log,
    last_report_log_path,
    write_last_report_log,
)
from inventory_parser.web_api import WebApi


def test_last_report_log_overwrites_previous_run() -> None:
    first = write_last_report_log(
        source="gui",
        config={"outputFormat": "html", "paths": ["one.txt"]},
        result={"ok": False, "error": "first error"},
        elapsed_seconds=1.0,
    )
    assert first is not None
    assert first.name == LOG_FILENAME
    assert "first error" in first.read_text(encoding="utf-8")

    second = write_last_report_log(
        source="gui",
        config={"outputFormat": "both", "paths": ["two.txt"]},
        result={"ok": True, "xlsx": r"C:\out.xlsx", "html": r"C:\out.html", "characterCount": 2},
        elapsed_seconds=3.2,
    )
    assert second == first
    text = second.read_text(encoding="utf-8")
    assert "first error" not in text
    assert "Status: ok" in text
    assert r"C:\out.xlsx" in text
    assert "two.txt" in text
    assert "Characters: 2" in text


def test_format_last_report_log_includes_error_and_traceback() -> None:
    text = format_last_report_log(
        source="gui",
        config={
            "includeSpells": True,
            "includeSlot2": True,
            "advancedWeights": True,
            "sessionWeights": {"ac": 10, "hp": 8},
        },
        result={"ok": False, "error": "Permission denied"},
        traceback_text="Traceback (most recent call last):\n  boom",
        elapsed_seconds=0.5,
    )
    assert "Status: failed" in text
    assert "Permission denied" in text
    assert "Traceback (most recent call last):" in text
    assert "Advanced weights: yes (2 stats)" in text
    assert "Spells: yes" in text


def test_generate_report_writes_last_report_log(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    inv = root / "Examples" / "Deflub_bristle-Inventory.txt"
    out = tmp_path / "solo.xlsx"
    result = WebApi()._generate_report_sync(
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
    log = last_report_log_path()
    assert log.is_file()
    text = log.read_text(encoding="utf-8")
    assert "Status: ok" in text
    assert "Source: gui" in text
    assert "Format: html" in text
    assert str(inv) in text
    assert result["html"] in text


def test_generate_report_failure_writes_error_log() -> None:
    result = WebApi()._generate_report_sync(
        {
            "paths": [],
            "outputPath": "",
            "includeSlot2": False,
        }
    )
    assert result["ok"] is False
    text = last_report_log_path().read_text(encoding="utf-8")
    assert "Status: failed" in text
    assert "Add at least one *-Inventory.txt" in text
