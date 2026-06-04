from inventory_parser.eq_servers import EQ_SERVER_DISPLAY_NAMES, server_display_name


def test_eq_server_table_includes_bristle() -> None:
    assert EQ_SERVER_DISPLAY_NAMES["bristle"] == "Bristlebane"


def test_server_display_name_case_insensitive_slug() -> None:
    assert server_display_name("BRISTLE") == "Bristlebane"
