from inventory_parser.spell_runes import (
    SpellLevelBlock,
    SpellRuneConfig,
    block_for_level,
    enabled_blocks,
    load_rune_config,
    rune_tier_for_level,
)


def test_load_default_config() -> None:
    cfg = load_rune_config()
    assert cfg.band_size == 5
    assert len(cfg.tiers) == 5
    assert len(enabled_blocks(cfg)) == 2


def test_tier_mapping_121_130() -> None:
    cfg = load_rune_config()
    assert rune_tier_for_level(121, cfg) == "Minor"
    assert rune_tier_for_level(122, cfg) == "Lesser"
    assert rune_tier_for_level(125, cfg) == "Glowing"
    assert rune_tier_for_level(126, cfg) == "Minor"
    assert rune_tier_for_level(130, cfg) == "Glowing"


def test_older_blocks_not_counted() -> None:
    cfg = load_rune_config()
    assert block_for_level(115, cfg) is not None
    assert rune_tier_for_level(115, cfg) is None
    assert rune_tier_for_level(120, cfg) is None


def test_future_block_131_135() -> None:
    cfg = load_rune_config()
    extended = SpellRuneConfig(
        band_size=cfg.band_size,
        tiers=cfg.tiers,
        blocks=cfg.blocks
        + (
            SpellLevelBlock(
                131,
                135,
                "131-135",
                ("Future expansion",),
                "TBD",
                True,
            ),
        ),
    )
    assert rune_tier_for_level(131, extended) == "Minor"
    assert rune_tier_for_level(135, extended) == "Glowing"
