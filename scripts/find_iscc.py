"""Print the path to Inno Setup ISCC.exe (one line), or exit 1 if missing."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _candidates() -> list[Path]:
    override = os.environ.get("IP_ISCC", "").strip()
    paths: list[Path] = []
    if override:
        paths.append(Path(override))
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    pf86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    for root in (local, pf86, pf):
        for ver in ("Inno Setup 6", "Inno Setup 7"):
            paths.append(root / ver / "ISCC.exe")
    return paths


def main() -> int:
    for path in _candidates():
        if path.is_file():
            print(path.resolve())
            return 0
    print("ERROR: ISCC.exe not found. Install Inno Setup 6 or set IP_ISCC.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
