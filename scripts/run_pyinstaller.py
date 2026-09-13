"""Invoke PyInstaller for the EQ Gear Management GUI (paths with spaces)."""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from package_version import exe_name_for_version, read_package_version

_ROOT = Path(__file__).resolve().parent.parent


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


def _write_version_info(path: Path, version: str, exe_name: str) -> None:
    a, b, c, d = _version_to_quad(version)
    quad_str = f"({a}, {b}, {c}, {d})"
    file_ver_str = f"{a}.{b}.{c}.{d}"
    orig = f"{exe_name}.exe"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={quad_str},
    prodvers={quad_str},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [
        StringStruct('CompanyName', 'Lubworks'),
        StringStruct('FileDescription', 'EQ Gear Management'),
        StringStruct('FileVersion', '{file_ver_str}'),
        StringStruct('InternalName', '{exe_name}'),
        StringStruct('LegalCopyright', 'Copyright © 2026 Lubworks'),
        StringStruct('OriginalFilename', '{orig}'),
        StringStruct('ProductName', 'EQ Gear Management'),
        StringStruct('ProductVersion', '{version}'),
        StringStruct('Comments', 'https://github.com/Neclub/EQ-Gear-Management')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""",
        encoding="utf-8",
    )


def zip_onedir_bundle(dist_dir: Path, exe_name: str) -> Path:
    """Zip dist/<name>/ to dist/<name>.zip with the folder as the zip root."""
    folder = dist_dir / exe_name
    if not folder.is_dir():
        raise FileNotFoundError(f"Onedir folder not found: {folder}")
    zip_path = dist_dir / f"{exe_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            arcname = path.relative_to(dist_dir).as_posix()
            zf.write(path, arcname=arcname)
    return zip_path


def pyinstaller_command(
    *,
    onefile: bool,
    version: str,
    exe_name: str,
    root: Path | None = None,
    python_exe: str | None = None,
) -> list[str]:
    project = root or _ROOT
    version_info = project / "build" / "EQGM_version_info.txt"
    _write_version_info(version_info, version, exe_name)
    entry = project / "scripts" / "pyinstaller_gui.py"
    args = [
        python_exe or sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile" if onefile else "--onedir",
        "--noconsole",
        "--noupx",
        "--name",
        exe_name,
        "--exclude-module",
        "numpy",
        "--exclude-module",
        "pandas",
        "--exclude-module",
        "matplotlib",
        "--collect-all",
        "webview",
        "--hidden-import",
        "webview.platforms.winforms",
        "--collect-data",
        "inventory_parser",
        "--hidden-import",
        "inventory_parser.data",
        "--hidden-import",
        "inventory_parser.package_data",
        "--distpath",
        str(project / "dist"),
        "--workpath",
        str(project / "build" / "pyinstaller"),
        "--specpath",
        str(project / "build"),
        str(entry),
    ]
    if sys.platform == "win32":
        args.extend(["--version-file", str(version_info.resolve())])
        icon_ico = project / "src" / "inventory_parser" / "assets" / "eq-icon.ico"
        if icon_ico.is_file():
            args.extend(["--icon", str(icon_ico.resolve())])
        manifest = project / "src" / "inventory_parser" / "assets" / "eqgm.manifest"
        if manifest.is_file():
            args.extend(["--manifest", str(manifest.resolve())])
    return args


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the EQGM Windows executable.")
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Pack a single-file exe (Windows Defender often flags this).",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Zip the onedir folder to dist/EQGM-x.y.z.zip (ignored with --onefile).",
    )
    parser.add_argument(
        "--zip-only",
        action="store_true",
        help="Zip an existing onedir folder without rebuilding.",
    )
    args = parser.parse_args(argv)

    version = read_package_version(_ROOT)
    exe_name = exe_name_for_version(version)
    dist = _ROOT / "dist"
    if args.zip_only:
        zip_path = zip_onedir_bundle(dist, exe_name)
        print(f"Zipped onedir: {zip_path}")
        return 0
    cmd = pyinstaller_command(onefile=args.onefile, version=version, exe_name=exe_name)
    dist = _ROOT / "dist"
    if args.onefile:
        print(f"Package version: {version}")
        print(f"Output exe: {dist / f'{exe_name}.exe'}")
    else:
        print(f"Package version: {version}")
        print(f"Output folder: {dist / exe_name}")
    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd, cwd=str(_ROOT))
    if rc != 0:
        return rc
    if args.zip and not args.onefile:
        zip_path = zip_onedir_bundle(dist, exe_name)
        print(f"Zipped onedir: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
