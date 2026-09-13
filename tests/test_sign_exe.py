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
    assert '"--onedir"' in text
    assert '"--onefile" if onefile else "--onedir"' in text


def test_pyinstaller_command_defaults_to_onedir() -> None:
    from run_pyinstaller import pyinstaller_command

    cmd = pyinstaller_command(onefile=False, version="1.0.0", exe_name="EQGM-1.0.0")
    assert "--onedir" in cmd
    assert "--onefile" not in cmd
    assert "--noupx" in cmd
    onefile_cmd = pyinstaller_command(onefile=True, version="1.0.0", exe_name="EQGM-1.0.0")
    assert "--onefile" in onefile_cmd
    assert "--onedir" not in onefile_cmd


def test_zip_onedir_bundle_overwrites(tmp_path: Path) -> None:
    from run_pyinstaller import zip_onedir_bundle

    folder = tmp_path / "EQGM-1.0.0"
    nested = folder / "_internal"
    nested.mkdir(parents=True)
    (folder / "EQGM-1.0.0.exe").write_bytes(b"MZ")
    (nested / "python.dll").write_bytes(b"dll")
    zip_path = zip_onedir_bundle(tmp_path, "EQGM-1.0.0")
    assert zip_path.is_file()
    import zipfile

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "EQGM-1.0.0/EQGM-1.0.0.exe" in names
    assert "EQGM-1.0.0/_internal/python.dll" in names


def test_release_workflow_ships_zip_after_optional_sign() -> None:
    workflow = (
        Path(__file__).resolve().parents[1] / ".github" / "workflows" / "build-release.yml"
    ).read_text(encoding="utf-8")
    assert "python scripts/run_pyinstaller.py --onefile" in workflow
    assert "python scripts/run_pyinstaller.py --zip-only" in workflow
    sign_at = workflow.index("Sign executable")
    zip_at = workflow.index("python scripts/run_pyinstaller.py --zip-only")
    assert sign_at < zip_at
    assert "dist/EQGM-${{ steps.version.outputs.version }}.zip" in workflow
