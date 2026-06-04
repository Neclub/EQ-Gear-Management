import importlib.metadata
import re
import subprocess
import sys
from pathlib import Path

from inventory_parser import __version__

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from package_version import exe_name_for_version


def test_exe_name_includes_version() -> None:
    assert exe_name_for_version(__version__) == f"InventoryParser-{__version__}"


def test_version_is_semver_like() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_installed_metadata_matches() -> None:
    assert importlib.metadata.version("inventory-parser") == __version__


def test_cli_version_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "inventory_parser", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert __version__ in result.stdout
