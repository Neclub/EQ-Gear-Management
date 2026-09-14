"""Invoke Nuitka standalone for the EQ Gear Management GUI."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from package_version import (
    APP_EXE_BASENAME,
    nuitka_dist_dir,
    read_package_version,
)

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
_ENTRY = _SCRIPTS / "pyinstaller_gui.py"


def _version_to_quad(version: str) -> tuple[int, int, int, int]:
    parts: list[int] = []
    for seg in version.split("."):
        num = ""
        for c in seg:
            if c.isdigit():
                num += c
            else:
                break
        parts.append(int(num) if num else 0)
        if len(parts) >= 4:
            break
    while len(parts) < 4:
        parts.append(0)
    return (parts[0], parts[1], parts[2], parts[3])


def main() -> int:
    version = read_package_version(_ROOT)
    a, b, c, d = _version_to_quad(version)
    quad_version = f"{a}.{b}.{c}.{d}"
    dist_dir = nuitka_dist_dir(_ROOT)
    out_exe = dist_dir / f"{APP_EXE_BASENAME}.exe"
    icon_ico = _SRC / "inventory_parser" / "assets" / "eq-icon.ico"

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{str(_SRC)};{existing_pythonpath}" if existing_pythonpath else str(_SRC)
    )

    args = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--assume-yes-for-downloads",
        "--windows-console-mode=disable",
        f"--output-filename={APP_EXE_BASENAME}.exe",
        "--include-package=openpyxl",
        "--include-package=inventory_parser",
        "--include-package-data=inventory_parser",
        # Let Nuitka's built-in pywebview plugin pick Windows backends only.
        # Do not force-include the whole webview.platforms tree (android/gtk
        # conflict with that plugin on Windows).
        "--include-package=pythonnet",
        "--include-package=clr_loader",
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=pandas",
        "--nofollow-import-to=matplotlib",
        f"--output-dir={str(_ROOT / 'dist')}",
        f"--file-version={quad_version}",
        f"--product-version={version}",
        "--windows-company-name=Lubworks",
        "--windows-file-description=EQ Gear Management",
        "--windows-product-name=EQ Gear Management",
        "--copyright=Copyright (c) 2026 Lubworks",
    ]

    if sys.platform == "win32" and icon_ico.is_file():
        args.append(f"--windows-icon-from-ico={str(icon_ico.resolve())}")

    # Entry point MUST be last.
    args.append(str(_ENTRY.resolve()))

    print(f"Package version: {version}")
    print(f"Standalone folder: {dist_dir}")
    print(f"Output exe: {out_exe}")
    print("Running:", " ".join(args))
    return subprocess.call(args, cwd=str(_ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
