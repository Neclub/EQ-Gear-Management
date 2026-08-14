"""Tests for bundled package data loading."""

from inventory_parser.package_data import asset_path, data_dir, gui_asset_path, read_data_text, read_gui_text


def test_data_dir_exists() -> None:
    assert data_dir().is_dir()


def test_gui_assets_exist() -> None:
    assert gui_asset_path("setup.html").is_file()
    assert gui_asset_path("setup.js").is_file()
    assert gui_asset_path("shared.css").is_file()
    assert gui_asset_path("class_visuals.js").is_file()
    assert "EQ Gear Management" in read_gui_text("setup.html")
    assert "ClassVisuals" in read_gui_text("class_visuals.js")


def test_app_icon_assets_exist() -> None:
    assert asset_path("eq-icon.png").is_file()
    assert asset_path("eq-icon.ico").is_file()


def test_read_spell_rune_config() -> None:
    text = read_data_text("spell_rune_bands.json")
    assert "blocks" in text


def test_read_vendor_json() -> None:
    text = read_data_text("sor_r1_vendor_items.json")
    assert "tier_code" in text
