# Backup — pre Missing Useful Spells (2026-07-10)

Snapshot before adding the Missing Useful Spells export tab.

## Files

- `export_bundle.py`
- `excel_export.py`
- `html_export.py`
- `cli.py`
- `web_api.py`
- `team_report.html`
- `test_excel_export.py`
- `test_html_export.py`

## Restore from this folder

```powershell
cd "C:\Users\120ch\Cursor Projects\Inventory Parser"
Copy-Item backup\pre-missing-useful-spells\export_bundle.py src\inventory_parser\export_bundle.py -Force
Copy-Item backup\pre-missing-useful-spells\excel_export.py src\inventory_parser\excel_export.py -Force
Copy-Item backup\pre-missing-useful-spells\html_export.py src\inventory_parser\html_export.py -Force
Copy-Item backup\pre-missing-useful-spells\cli.py src\inventory_parser\cli.py -Force
Copy-Item backup\pre-missing-useful-spells\web_api.py src\inventory_parser\web_api.py -Force
Copy-Item backup\pre-missing-useful-spells\team_report.html src\inventory_parser\data\team_report.html -Force
Copy-Item backup\pre-missing-useful-spells\test_excel_export.py tests\test_excel_export.py -Force
Copy-Item backup\pre-missing-useful-spells\test_html_export.py tests\test_html_export.py -Force
```

Also remove new files if rolling back fully:

```powershell
Remove-Item src\inventory_parser\useful_spells.py -ErrorAction SilentlyContinue
Remove-Item src\inventory_parser\data\useful_spells.json -ErrorAction SilentlyContinue
Remove-Item scripts\convert_useful_spells.py -ErrorAction SilentlyContinue
Remove-Item tests\test_useful_spells.py -ErrorAction SilentlyContinue
```
