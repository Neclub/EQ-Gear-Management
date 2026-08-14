"""Sign a Windows executable with Authenticode (optional post-PyInstaller step)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_DEFAULT_TIMESTAMP = "http://timestamp.digicert.com"


def _find_signtool() -> Path | None:
    override = os.environ.get("IP_SIGNTOOL", "").strip()
    if override:
        path = Path(override)
        return path if path.is_file() else None

    kits_root = Path(r"C:\Program Files (x86)\Windows Kits\10\bin")
    if not kits_root.is_dir():
        return None

    version_dirs = sorted(
        (p for p in kits_root.iterdir() if p.is_dir() and p.name[:1].isdigit()),
        key=lambda p: p.name,
        reverse=True,
    )
    for version_dir in version_dirs:
        for arch in ("x64", "x86", "arm64"):
            candidate = version_dir / arch / "signtool.exe"
            if candidate.is_file():
                return candidate
    return None


def _signing_configured() -> bool:
    pfx = os.environ.get("IP_SIGN_PFX", "").strip()
    thumbprint = os.environ.get("IP_SIGN_THUMBPRINT", "").strip()
    return bool(pfx or thumbprint)


def _build_sign_args(exe_path: Path, signtool: Path) -> list[str]:
    timestamp = os.environ.get("IP_SIGN_TIMESTAMP_URL", _DEFAULT_TIMESTAMP).strip()
    args = [
        str(signtool),
        "sign",
        "/fd",
        "SHA256",
        "/td",
        "SHA256",
        "/tr",
        timestamp,
        "/v",
    ]

    pfx = os.environ.get("IP_SIGN_PFX", "").strip()
    thumbprint = os.environ.get("IP_SIGN_THUMBPRINT", "").strip()
    if pfx:
        pfx_path = Path(pfx)
        if not pfx_path.is_file():
            raise FileNotFoundError(f"Signing certificate not found: {pfx_path}")
        args.extend(["/f", str(pfx_path.resolve())])
        password = os.environ.get("IP_SIGN_PASSWORD", "")
        if password:
            args.extend(["/p", password])
    elif thumbprint:
        args.extend(["/sha1", thumbprint])
    else:
        raise RuntimeError("No signing certificate configured.")

    args.append(str(exe_path.resolve()))
    return args


def sign_executable(exe_path: Path, *, required: bool = False) -> int:
    if not exe_path.is_file():
        print(f"ERROR: Executable not found: {exe_path}", file=sys.stderr)
        return 1

    if not _signing_configured():
        if required:
            print(
                "ERROR: Code signing is required but not configured.\n"
                "Set IP_SIGN_PFX (and IP_SIGN_PASSWORD) or IP_SIGN_THUMBPRINT,\n"
                "or copy codesign.local.bat.example to codesign.local.bat.",
                file=sys.stderr,
            )
            return 1
        print(
            "Skipping code signing (not configured).\n"
            "To sign releases, copy codesign.local.bat.example to codesign.local.bat."
        )
        return 0

    signtool = _find_signtool()
    if signtool is None:
        msg = (
            "ERROR: signtool.exe not found. Install the Windows SDK or set IP_SIGNTOOL "
            "to the full path of signtool.exe."
        )
        print(msg, file=sys.stderr)
        return 1

    try:
        sign_args = _build_sign_args(exe_path, signtool)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Signing: {exe_path}")
    print(f"Using: {signtool}")
    result = subprocess.run(sign_args, check=False)
    if result.returncode != 0:
        print("ERROR: signtool failed.", file=sys.stderr)
        return result.returncode

    print("Code signing succeeded.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sign an EQGM release exe.")
    parser.add_argument("exe", type=Path, help="Path to the .exe to sign")
    parser.add_argument(
        "--require",
        action="store_true",
        help="Fail if signing is not configured (also enabled by IP_SIGN_REQUIRED=1)",
    )
    args = parser.parse_args(argv)
    required = args.require or os.environ.get("IP_SIGN_REQUIRED", "").strip() in {
        "1",
        "true",
        "True",
        "yes",
        "YES",
    }
    return sign_executable(args.exe, required=required)


if __name__ == "__main__":
    raise SystemExit(main())
