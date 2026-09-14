import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from package_version import (
    APP_EXE_BASENAME,
    installer_name_for_version,
    nuitka_dist_dir,
)
from sign_exe import sign_executable


def test_sign_skips_when_not_configured(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "EQGM.exe"
    exe.write_bytes(b"MZ")
    monkeypatch.delenv("IP_SIGN_PFX", raising=False)
    monkeypatch.delenv("IP_SIGN_THUMBPRINT", raising=False)
    monkeypatch.delenv("IP_SIGN_REQUIRED", raising=False)
    assert sign_executable(exe) == 0


def test_sign_required_fails_without_config(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "EQGM.exe"
    exe.write_bytes(b"MZ")
    monkeypatch.delenv("IP_SIGN_PFX", raising=False)
    monkeypatch.delenv("IP_SIGN_THUMBPRINT", raising=False)
    assert sign_executable(exe, required=True) == 1


def test_sign_fails_when_exe_missing(monkeypatch) -> None:
    monkeypatch.setenv("IP_SIGN_PFX", r"C:\missing\cert.pfx")
    assert sign_executable(Path(r"C:\missing\app.exe")) == 1


def test_nuitka_packaging_uses_stable_exe_and_webview() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_pyinstaller.py"
    text = script.read_text(encoding="utf-8")
    args_blob = text[text.index("args = [") : text.index("if sys.platform")]
    assert "nuitka" in text
    assert "--standalone" in args_blob
    assert 'f"--output-filename={APP_EXE_BASENAME}.exe"' in args_blob
    assert "--include-package=webview" not in args_blob
    assert "--include-package=webview.platforms" not in args_blob
    assert "--include-module=webview.platforms.winforms" not in args_blob
    assert "pywebview plugin" in text
    assert "--include-package=pythonnet" in args_blob
    assert "--include-package=clr_loader" in args_blob
    assert "--include-package-data=inventory_parser" in args_blob
    assert "--nofollow-import-to=numpy" in args_blob
    assert "windows-company-name=Lubworks" in args_blob
    assert "Copyright" in args_blob
    assert installer_name_for_version("1.35.11") == "EQGM-install-1.35.11"
    assert nuitka_dist_dir(root) == root / "dist" / "pyinstaller_gui.dist"
    assert APP_EXE_BASENAME == "EQGM"


def test_inno_installer_script_matches_eqlogparser_layout() -> None:
    root = Path(__file__).resolve().parents[1]
    iss = (root / "installer" / "EQGM.iss").read_text(encoding="utf-8")
    assert "EQGM-install-{#MyAppVersion}" in iss
    assert r"{commonpf}\{#MyAppName}" in iss
    assert 'MyAppExeName "EQGM.exe"' in iss
    assert "CloseApplications=yes" in iss
    assert "desktopicon" in iss
    assert "LaunchProgram" in iss
    assert "69213E35-8BA0-4151-A501-6A71CE54E716" in iss
