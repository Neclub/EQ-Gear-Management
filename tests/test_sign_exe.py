import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sign_exe import sign_executable


def test_sign_skips_when_not_configured(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "EQGM-1.0.0.exe"
    exe.write_bytes(b"MZ")
    monkeypatch.delenv("IP_SIGN_PFX", raising=False)
    monkeypatch.delenv("IP_SIGN_THUMBPRINT", raising=False)
    monkeypatch.delenv("IP_SIGN_REQUIRED", raising=False)
    assert sign_executable(exe) == 0


def test_sign_required_fails_without_config(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "EQGM-1.0.0.exe"
    exe.write_bytes(b"MZ")
    monkeypatch.delenv("IP_SIGN_PFX", raising=False)
    monkeypatch.delenv("IP_SIGN_THUMBPRINT", raising=False)
    assert sign_executable(exe, required=True) == 1


def test_sign_fails_when_exe_missing(monkeypatch) -> None:
    monkeypatch.setenv("IP_SIGN_PFX", r"C:\missing\cert.pfx")
    assert sign_executable(Path(r"C:\missing\app.exe")) == 1


def test_pyinstaller_packaging_avoids_upx_and_identifies_publisher() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_pyinstaller.py"
    text = script.read_text(encoding="utf-8")
    assert "--noupx" in text
    assert "--manifest" in text
    assert "eqgm.manifest" in text
    assert "https://github.com/Neclub/EQ-Gear-Management" in text
