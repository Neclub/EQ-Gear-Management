@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
for /f "delims=" %%V in ('py "%~dp0scripts\print_package_version.py"') do set "IP_VER=%%V"
set "OUT_DIR=%~dp0dist\EQGM-%IP_VER%"
set "OUT_DIR_EXE=%OUT_DIR%\EQGM-%IP_VER%.exe"
set "OUT_EXE=%~dp0dist\EQGM-%IP_VER%.exe"
set "OUT_ZIP=%~dp0dist\EQGM-%IP_VER%.zip"

echo EQ Gear Management - build executable
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
echo Building folder bundle (avoids Windows Defender one-file false positives)...
py -3 "%~dp0scripts\run_pyinstaller.py" --zip
if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller onedir failed. See messages above.
  pause
  exit /b 1
)

echo.
echo Building single-file exe (in-app update checks from older builds)...
py -3 "%~dp0scripts\run_pyinstaller.py" --onefile
if errorlevel 1 (
  echo.
  echo ERROR: PyInstaller onefile failed. See messages above.
  pause
  exit /b 1
)

if not exist "%OUT_DIR_EXE%" (
  echo.
  echo ERROR: Onedir exe was not created:
  echo   %OUT_DIR_EXE%
  pause
  exit /b 1
)

if not exist "%OUT_EXE%" (
  echo.
  echo ERROR: Single-file exe was not created:
  echo   %OUT_EXE%
  pause
  exit /b 1
)

if exist "%~dp0codesign.local.bat" (
  echo.
  echo Loading local code signing settings...
  call "%~dp0codesign.local.bat"
)

echo.
py -3 "%~dp0scripts\sign_exe.py" "%OUT_DIR_EXE%"
if errorlevel 1 (
  echo.
  echo ERROR: Code signing failed.
  pause
  exit /b 1
)
py -3 "%~dp0scripts\sign_exe.py" "%OUT_EXE%"
if errorlevel 1 (
  echo.
  echo ERROR: Code signing failed.
  pause
  exit /b 1
)
py -3 "%~dp0scripts\run_pyinstaller.py" --zip-only
if errorlevel 1 (
  echo.
  echo ERROR: Zipping the folder bundle failed.
  pause
  exit /b 1
)

echo.
echo Build succeeded.
echo.
echo   %OUT_ZIP%  (recommended download)
echo   %OUT_EXE%  (single-file; Windows Defender may flag this)
echo.
echo Opening dist folder in Explorer...
explorer /select,"%OUT_ZIP%"
endlocal
exit /b 0
