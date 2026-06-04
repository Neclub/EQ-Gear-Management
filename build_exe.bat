@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "OUT_EXE="
echo.
for /f "delims=" %%V in ('py "%~dp0scripts\print_package_version.py"') do set "IP_VER=%%V"
set "OUT_EXE=%~dp0dist\InventoryParser-%IP_VER%.exe"

echo Inventory Parser - build executable
echo Version: %IP_VER%
echo Project folder: %~dp0
echo.

echo Installing package (editable) and PyInstaller...
py -3 -m pip install -q -e "%~dp0."
if errorlevel 1 (
  echo.
  echo ERROR: pip install -e . failed. Use Python 3.10+ with the py launcher.
  pause
  exit /b 1
)
py -3 -m pip install -q "pyinstaller>=6.0"
if errorlevel 1 (
  echo.
  echo ERROR: pip install pyinstaller failed.
  pause
  exit /b 1
)

echo.
echo Building single-file GUI executable (no console window)...
py -3 "%~dp0scripts\run_pyinstaller.py"
if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller failed. See messages above.
  pause
  exit /b 1
)

if not exist "%OUT_EXE%" (
  echo.
  echo ERROR: Build reported success but exe was not created:
  echo   %OUT_EXE%
  echo.
  echo The exe is NOT in build\ — only intermediate files are there.
  pause
  exit /b 1
)

if exist "%~dp0codesign.local.bat" (
  echo.
  echo Loading local code signing settings...
  call "%~dp0codesign.local.bat"
)

echo.
py -3 "%~dp0scripts\sign_exe.py" "%OUT_EXE%"
if errorlevel 1 (
  echo.
  echo ERROR: Code signing failed.
  pause
  exit /b 1
)

echo.
echo Build succeeded.
echo.
echo   %OUT_EXE%  (version %IP_VER%)
echo.
echo Opening dist folder in Explorer...
explorer /select,"%OUT_EXE%"
endlocal
exit /b 0
