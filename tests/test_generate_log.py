from pathlib import Path

import pytest
import urllib.error

from inventory_parser.generate_log import (
    LOG_FILENAME,
    FetchSnapshot,
    fetch_recording,
    format_last_report_log,
    last_report_log_path,
    record_cache,
    record_problem,
    record_website,
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
    assert "Fetches" in text
    assert "Problems" in text


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
    assert "Fetches" in text
    assert "Cache" in text
    assert "Website" in text
    assert "Problems" in text


def test_format_last_report_log_includes_fetch_snapshot() -> None:
    snap = FetchSnapshot(
        cache_counts={"Gear T-levels": 3, "Type 7/8 catalog": 1, "Item icons": 2},
        cache_details={"Type 7/8 catalog": ["dex", "int"]},
        website_urls=[
            "https://items.eqresource.com/items.php?id=111665",
            "https://items.eqresource.com/itemimages/5297.png",
            "https://sor.eqresource.com/raidarmor.php",
        ],
        problems=["https://items.eqresource.com/items.php?id=9: timed out"],
    )
    text = format_last_report_log(
        source="gui",
        config={"outputFormat": "html"},
        result={"ok": True, "warnings": ["some warning"]},
        traceback_text=None,
        elapsed_seconds=1.0,
        fetch_snapshot=snap,
    )
    assert "Fetches" in text
    assert "Gear T-levels: 3" in text
    assert "Type 7/8 catalog: dex, int" in text
    assert "Item icons: 2" in text
    assert "Item pages (1)" in text
    assert "https://items.eqresource.com/items.php?id=111665" in text
    assert "Item icons (1)" in text
    assert "Raid BiS pages (1)" in text
    assert "timed out" in text
    assert "some warning" in text


def test_format_dedupes_problems_already_in_warnings() -> None:
    msg = "Live EQ Resource search failed; using cached search."
    text = format_last_report_log(
        source="cli",
        config={},
        result={"ok": True, "warnings": [msg]},
        traceback_text=None,
        elapsed_seconds=0.1,
        fetch_snapshot=FetchSnapshot(problems=[msg, "extra problem"]),
    )
    assert "extra problem" in text
    # Warning section still has it; Problems should not repeat the same string.
    problems_section = text.split("Problems")[1].split("Error")[0]
    assert msg not in problems_section
    assert "extra problem" in problems_section


def test_fetch_recording_context_collects_and_noops_outside() -> None:
    record_cache("Gear T-levels")
    record_website("https://items.eqresource.com/items.php?id=1")
    record_problem("should not stick")
    with fetch_recording() as recorder:
        record_cache("Gear T-levels")
        record_cache("Gear T-levels")
        record_cache("Type 7/8 catalog", "dex")
        record_website("https://items.eqresource.com/items.php?id=1")
        record_website("https://items.eqresource.com/items.php?id=1")
        record_problem("boom")
        record_problem("boom")
        snap = recorder.snapshot()
    assert snap.cache_counts["Gear T-levels"] == 2
    assert snap.cache_details["Type 7/8 catalog"] == ["dex"]
    assert snap.website_urls == ["https://items.eqresource.com/items.php?id=1"]
    assert snap.problems == ["boom"]
    # Outside context: no-ops
    record_cache("Item icons")
    assert recorder.snapshot().cache_counts.get("Item icons") is None


def test_http_bytes_records_website_and_problems(monkeypatch) -> None:
    from inventory_parser import http_fetch

    class _Resp:
        def geturl(self):
            return "https://items.eqresource.com/items.php?id=1"

        def read(self, _n):
            return b"ok"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _Opener:
        def open(self, req, timeout=0):
            return _Resp()

    monkeypatch.setattr(
        http_fetch.urllib.request, "build_opener", lambda *_a, **_k: _Opener()
    )
    with fetch_recording() as recorder:
        data = http_fetch.http_get_bytes(
            "https://items.eqresource.com/items.php?id=1",
            timeout=1,
            user_agent="test",
        )
        assert data == b"ok"
        snap = recorder.snapshot()
    assert snap.website_urls == ["https://items.eqresource.com/items.php?id=1"]
    assert snap.problems == []

    class _FailOpener:
        def open(self, req, timeout=0):
            raise urllib.error.URLError("timed out")

    monkeypatch.setattr(
        http_fetch.urllib.request, "build_opener", lambda *_a, **_k: _FailOpener()
    )
    with fetch_recording() as recorder:
        with pytest.raises(urllib.error.URLError):
            http_fetch.http_get_bytes(
                "https://items.eqresource.com/items.php?id=2",
                timeout=1,
                user_agent="test",
            )
        snap = recorder.snapshot()
    assert snap.website_urls == []
    assert any("items.php?id=2" in p and "timed out" in p for p in snap.problems)


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
    assert "Fetches" in text
    assert "Cache" in text
    assert "Website" in text
    assert "Problems" in text


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
    assert "Fetches" in text
    assert "Problems" in text
