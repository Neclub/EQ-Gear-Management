# GUI backup — pre pywebview HTML GUI (2026-06-14)

Snapshot of the tkinter GUI before migration to pywebview + HTML shell.

## Files

- `gui.py` — main window layout and theme
- `pill_button.py` — pill-shaped button widget
- `gui_theme.py` — color constants
- `window_chrome.py` — Windows dark title bar
- `pyinstaller_gui.py` — PyInstaller entry (tkinter)
- `run_pyinstaller.py` — PyInstaller build script (pre-webview)
- `pyproject.toml` — dependencies (Pillow, gui:main entry)

## Restore from this folder

```powershell
cd "C:\Users\120ch\Cursor Projects\Inventory Parser"
Copy-Item backup\pre-pywebview-gui\gui.py src\inventory_parser\gui.py -Force
Copy-Item backup\pre-pywebview-gui\pill_button.py src\inventory_parser\pill_button.py -Force
Copy-Item backup\pre-pywebview-gui\gui_theme.py src\inventory_parser\gui_theme.py -Force
Copy-Item backup\pre-pywebview-gui\window_chrome.py src\inventory_parser\window_chrome.py -Force
Copy-Item backup\pre-pywebview-gui\pyinstaller_gui.py scripts\pyinstaller_gui.py -Force
Copy-Item backup\pre-pywebview-gui\run_pyinstaller.py scripts\run_pyinstaller.py -Force
Copy-Item backup\pre-pywebview-gui\pyproject.toml pyproject.toml -Force
# Remove HTML GUI modules if present:
Remove-Item src\inventory_parser\web_gui.py -ErrorAction SilentlyContinue
Remove-Item src\inventory_parser\web_api.py -ErrorAction SilentlyContinue
Remove-Item src\inventory_parser\web_bridge.py -ErrorAction SilentlyContinue
Remove-Item -Recurse src\inventory_parser\data\gui -ErrorAction SilentlyContinue
```

Then reinstall and restart:

```powershell
py -3 -m pip install -e .
py -3 -m inventory_parser.gui
```

## Restore from git (path-scoped)

Branch `backup/pre-pywebview-gui` and tag `backup/pre-pywebview-gui-2026-06-14` point at the commit before the HTML GUI migration:

```powershell
git fetch origin
git checkout origin/backup/pre-pywebview-gui -- src/inventory_parser/gui.py src/inventory_parser/pill_button.py src/inventory_parser/gui_theme.py src/inventory_parser/window_chrome.py scripts/pyinstaller_gui.py scripts/run_pyinstaller.py pyproject.toml
```

Restore `inventory-parser-gui = "inventory_parser.gui:main"` in `pyproject.toml` if needed, then remove web GUI files as above.

## Full rollback on main

To undo the HTML GUI merge on `main`, either:

1. Revert the migration commit(s): `git revert <commit-hash>`
2. Or check out the backup tag in a new branch and open a PR to restore tkinter

After restoring tkinter, push a revert commit to `main` — do not force-push unless you explicitly intend to rewrite history.
