# HTML export backup — pre sidebar redesign (2026-06-13)

Snapshot of the HTML report template and export module before mockup-1 sidebar navigator changes.

## Files

- `team_report.html` — self-contained HTML template (horizontal tabs layout)
- `html_export.py` — report JSON serialization and write helper

## Restore from this folder

```powershell
cd "C:\Users\120ch\Cursor Projects\Inventory Parser"
Copy-Item backup\pre-html-redesign\team_report.html src\inventory_parser\data\team_report.html -Force
Copy-Item backup\pre-html-redesign\html_export.py src\inventory_parser\html_export.py -Force
```

Then run tests: `pytest tests/test_html_export.py -q`

## Restore from git

Branch `backup/pre-html-redesign` points at the commit before the HTML redesign:

```powershell
git checkout backup/pre-html-redesign -- src/inventory_parser/data/team_report.html src/inventory_parser/html_export.py
```
