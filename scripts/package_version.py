"""Read EQGM package version from src for build scripts."""
from __future__ import annotations

import re
from pathlib import Path

APP_EXE_BASENAME = "EQGM"
_ENTRY_STEM = "pyinstaller_gui"


def read_package_version(root: Path | None = None) -> str:
    if root is None:
        root = Path(__file__).resolve().parent.parent
    init_py = root / "src" / "inventory_parser" / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        raise RuntimeError(f"Could not parse __version__ from {init_py}")
    return m.group(1).strip()


def exe_name_for_version(version: str, basename: str = APP_EXE_BASENAME) -> str:
    """Legacy portable name (EQGM-x.y.z). Prefer APP_EXE_BASENAME for installs."""
    return f"{basename}-{version}"


def installer_name_for_version(
    version: str, basename: str = APP_EXE_BASENAME
) -> str:
    """Release asset basename without extension: EQGM-install-x.y.z."""
    return f"{basename}-install-{version}"


def nuitka_dist_dir(root: Path | None = None) -> Path:
    """Nuitka --standalone output folder for scripts/pyinstaller_gui.py."""
    if root is None:
        root = Path(__file__).resolve().parent.parent
    return root / "dist" / f"{_ENTRY_STEM}.dist"


def app_exe_path(root: Path | None = None) -> Path:
    return nuitka_dist_dir(root) / f"{APP_EXE_BASENAME}.exe"
