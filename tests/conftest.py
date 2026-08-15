"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from inventory_parser.slot2_augs import chest_class, eqresource_gear_tier


@pytest.fixture(autouse=True)
def _no_live_chest_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests offline: only parse chest class from explicit HTML overrides."""
    original = chest_class.fetch_item_classes

    def _fetch(
        item_id: int,
        *,
        force_refresh: bool = False,
        raidloot_html: str | None = None,
        eqr_html: str | None = None,
        skip_cache_write: bool = False,
    ) -> list[str]:
        if raidloot_html is not None or eqr_html is not None:
            return original(
                item_id,
                force_refresh=force_refresh,
                raidloot_html=raidloot_html,
                eqr_html=eqr_html,
                skip_cache_write=skip_cache_write,
            )
        return []

    monkeypatch.setattr(chest_class, "fetch_item_classes", _fetch)


@pytest.fixture(autouse=True)
def _no_live_eqr_gear_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests offline: only parse T-codes from explicit HTML overrides."""
    original = eqresource_gear_tier.fetch_item_gear_tier

    def _fetch(
        item_id: int,
        *,
        force_refresh: bool = False,
        html_override: str | None = None,
        skip_cache_write: bool = False,
        allow_network: bool = True,
    ) -> str | None:
        if html_override is not None:
            return original(
                item_id,
                force_refresh=force_refresh,
                html_override=html_override,
                skip_cache_write=skip_cache_write,
                allow_network=False,
            )
        return None

    monkeypatch.setattr(eqresource_gear_tier, "fetch_item_gear_tier", _fetch)
