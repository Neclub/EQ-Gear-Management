"""Tests for bundled package data loading."""

from inventory_parser.package_data import data_dir, read_data_text


def test_data_dir_exists() -> None:
    assert data_dir().is_dir()


def test_read_spell_rune_config() -> None:
    text = read_data_text("spell_rune_bands.json")
    assert "blocks" in text


def test_read_vendor_json() -> None:
    text = read_data_text("sor_r1_vendor_items.json")
    assert "tier_code" in text
