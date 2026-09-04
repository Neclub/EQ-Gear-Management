"""Tests for determinate generate progress reporting."""

from __future__ import annotations

from pathlib import Path

from inventory_parser.slot2_augs.build import build_slot2_export
from inventory_parser.team_report import build_team_report

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "raidloot_dex_sample.html"


def test_build_slot2_export_progress_is_monotonic(tmp_path: Path):
    inv = tmp_path / "Proglub_test-ROG-Inventory.txt"
    inv.write_text(
        "Location\tName\tID\tCount\tSlots\n"
        "Head\tTest Helm\t1\t1\t6\n"
        "Head-Slot2\tEmpty\t0\t0\t0\n"
        "Charm\tTest Charm\t2\t1\t6\n"
        "Charm-Slot2\tEmpty\t0\t0\t0\n",
        encoding="utf-8",
    )
    html = FIXTURE.read_text(encoding="utf-8")
    events: list[dict] = []
    team = build_team_report([inv])

    bundle = build_slot2_export(
        team,
        catalog_html=html,
        fetch_eqr_augs=False,
        fetch_chest_class=False,
        fetch_expansions=False,
        include_anniversary=False,
        type78_slot_by_parent_id={1: 2, 2: 2},
        on_progress=events.append,
    )

    assert bundle.characters
    assert events
    assert all("message" in e and "fraction" in e for e in events)
    messages = [str(e["message"]) for e in events]
    assert all("Fetching raidloot catalog" not in m for m in messages)
    assert any("Fetching from" in m or "Using cached" in m for m in messages)
    fractions = [float(e["fraction"]) for e in events]
    assert fractions[0] >= 0.0
    assert fractions[-1] == 0.95
    assert all(0.0 <= f <= 1.0 for f in fractions)
    assert all(a <= b for a, b in zip(fractions, fractions[1:]))


def test_raid_bis_progress_names_source():
    from inventory_parser.raid_bis.build import build_raid_bis_export

    examples = Path(__file__).resolve().parents[1] / "Examples"
    fixtures = Path(__file__).resolve().parent / "fixtures"
    inv = examples / "Deflub_bristle-Inventory.txt"
    team = build_team_report([inv])
    events: list[dict] = []
    build_raid_bis_export(
        team,
        on_progress=events.append,
        allow_network=False,
        html_overrides={
            "raidarmor": (fixtures / "eqresource_raidarmor_sor.html").read_text(
                encoding="utf-8"
            ),
            "raidgear:back": (fixtures / "eqresource_raidgear_sor.html").read_text(
                encoding="utf-8"
            ),
            "raidvendor": (fixtures / "eqresource_raidvendor_sor.html").read_text(
                encoding="utf-8"
            ),
        },
        hydrate=False,
        embed_icons=False,
    )
    assert events
    messages = [str(e["message"]) for e in events]
    assert any("Fetching from EQ Resource" in m for m in messages)
    assert not any("Fetching current-expansion raid gear catalog" in m for m in messages)
    assert any("Comparing equipped gear to Raid BiS" in m for m in messages)
    fractions = [float(e["fraction"]) for e in events]
    assert all(0.0 <= f <= 1.0 for f in fractions)
    assert all(a <= b for a, b in zip(fractions, fractions[1:]))
