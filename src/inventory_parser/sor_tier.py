"""Shattering of Ro (SOR) tier gap labels for the upgrade tracking sheet."""

from __future__ import annotations

from inventory_parser.evolver import EVOLVER_GAP_LABEL
from inventory_parser.gear_tiers import UNKNOWN_TIER_LABEL, classify_gear_tier

# Kept for callers/tests that still import legacy marker names.
MARKER_BELOW_SOR_T2 = "SOR T2<"
MARKER_BELOW_SOR_T1 = "SOR T1/<"


def sor_gap_label(item_name: str | None, *, is_evolver: bool = False) -> str | None:
    """
    Return a tier code for equipped gear on the Gear T-Level sheet.

    - ``None`` — empty slot
    - ``Evolver`` — equipped Evolver item
    - tier code — e.g. ``SOR-R2``, ``TOB-R2``, ``LS-G1``, ``SOR-R1``
    - ``???`` — equipped but unrecognized
    """
    if not item_name:
        return None

    tier = classify_gear_tier(item_name)
    if tier is not None:
        return tier.code
    if is_evolver:
        return EVOLVER_GAP_LABEL
    return UNKNOWN_TIER_LABEL


def sor_gap_marker(item_name: str | None, *, is_evolver: bool = False) -> str | None:
    """Backward-compatible alias for :func:`sor_gap_label`."""
    return sor_gap_label(item_name, is_evolver=is_evolver)
