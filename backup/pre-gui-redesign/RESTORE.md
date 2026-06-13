# GUI backup — pre redesign (2026-06-12)

Snapshot of the GUI before mockup-based layout changes.

## Files

- `gui.py` — main window layout and theme
- `pill_button.py` — pill-shaped button widget

## Restore from this folder

```powershell
cd "C:\Users\120ch\Cursor Projects\Inventory Parser"
Copy-Item backup\pre-gui-redesign\gui.py src\inventory_parser\gui.py -Force
Copy-Item backup\pre-gui-redesign\pill_button.py src\inventory_parser\pill_button.py -Force
```

Then restart the app (`run_gui.bat` or `inventory-parser-gui`).

## Restore from git

Branch and tag point at commit `01e2280` (or whatever `backup/pre-gui-redesign` indicates):

```powershell
git checkout backup/pre-gui-redesign -- src/inventory_parser/gui.py src/inventory_parser/pill_button.py
```

Or reset the whole repo to the tag (discards other local changes):

```powershell
git checkout backup/pre-gui-redesign-2026-06-12
```
