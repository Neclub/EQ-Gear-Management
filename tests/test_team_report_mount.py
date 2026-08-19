"""Tests for in-app report viewer HTML bootstrap."""

import json

from inventory_parser.export_bundle import build_export_bundle
from inventory_parser.html_export import extract_report_json, serialize_report, write_team_html
from inventory_parser.web_bridge import report_viewer_html


def test_report_viewer_html_injects_payload() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    examples = root / "Examples"
    inv_files = sorted(examples.glob("*-Inventory.txt"))[:2]
    bundle = build_export_bundle([p.resolve() for p in inv_files], include_spells=False, include_achievements=False, include_slot2=False)
    payload = serialize_report(bundle)
    html = report_viewer_html(json.dumps(payload, ensure_ascii=False))
    assert "/*__REPORT_JSON__*/" not in html
    assert "mountReport" not in html or "if (REPORT)" in html
    parsed = extract_report_json(html)
    assert parsed["meta"]["characterCount"] == payload["meta"]["characterCount"]
    assert "</script>" not in html.split("const REPORT = ", 1)[1].split(";\n", 1)[0]


def test_write_team_html_still_boots() -> None:
    from pathlib import Path
    import tempfile

    root = Path(__file__).resolve().parents[1]
    examples = root / "Examples"
    inv = next(examples.glob("*-Inventory.txt"))
    bundle = build_export_bundle([inv.resolve()], include_spells=False, include_achievements=False, include_slot2=False)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "Team.html"
        write_team_html(bundle, out)
        text = out.read_text(encoding="utf-8")
        assert "if (REPORT)" in text
        parsed = extract_report_json(text)
        assert parsed["sections"]
