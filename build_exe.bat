@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "OUT_INSTALLER="
echo.
for /f "delims=" %%V in ('py "%~dp0scripts\print_package_version.py"') do set "IP_VER=%%V"
set "OUT_EXE=%~dp0dist\pyinstaller_gui.dist\EQGM.exe"
set "OUT_INSTALLER=%~dp0dist\EQGM-install-%IP_VER%.exe"

echo EQ Gear Management - build installer
echo Version: %IP_VER%
echo Project folder: %~dp0
echo.

echo Installing package (editable) and Nuitka...
py -3 -m pip install -q -e "%~dp0."
if errorlevel 1 (
  echo.
  echo ERROR: pip install -e . failed. Use Python 3.10+ with the py launcher.
  pause
  exit /b 1
)
py -3 -m pip install -q "nuitka>=2.0"
if errorlevel 1 (
  echo.
  echo ERROR: pip install nuitka failed.
  pause
  exit /b 1
)

echo.
echo Building Nuitka standalone GUI...
py -3 "%~dp0scripts\run_pyinstaller.py"
if errorlevel 1 (
  echo.
  echo ERROR: Nuitka failed. See messages above.
  pause
  exit /b 1
)

if not exist "%OUT_EXE%" (
  echo.
  echo ERROR: Build reported success but exe was not created:
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
echo Signing application exe (if configured)...
py -3 "%~dp0scripts\sign_exe.py" "%OUT_EXE%"
if errorlevel 1 (
  echo.
  echo ERROR: Code signing failed for EQGM.exe.
  pause
  exit /b 1
)

set "ISCC="
set "ISCC_TXT=%TEMP%\eqgm_iscc_path.txt"
py -3 "%~dp0scripts\find_iscc.py" > "%ISCC_TXT%"
if errorlevel 1 (
  echo.
  echo ERROR: Inno Setup compiler ^(ISCC.exe^) not found.
  echo Install Inno Setup 6 from https://jrsoftware.org/isinfo.php then re-run this script.
  echo Or set IP_ISCC to the full path of ISCC.exe.
  pause
  exit /b 1
)
set /p ISCC=<"%ISCC_TXT%"
del "%ISCC_TXT%" >nul 2>&1
if not defined ISCC goto :iscc_missing
if not exist "%ISCC%" goto :iscc_missing
echo Using Inno Setup: !ISCC!

echo.
echo Building installer with Inno Setup...
"!ISCC!" /DMyAppVersion=!IP_VER! "%~dp0installer\EQGM.iss"
if errorlevel 1 (
  echo.
  echo ERROR: Inno Setup compile failed.
  pause
  exit /b 1
)

if not exist "%OUT_INSTALLER%" (
  echo.
  echo ERROR: Installer was not created:
  echo   %OUT_INSTALLER%
  pause
  exit /b 1
)

echo.
echo Signing installer (if configured)...
py -3 "%~dp0scripts\sign_exe.py" "%OUT_INSTALLER%"
if errorlevel 1 (
  echo.
  echo ERROR: Code signing failed for installer.
  pause
  exit /b 1
)

echo.
echo Build succeeded.
echo.
echo   %OUT_INSTALLER%  (version %IP_VER%)
echo.
echo Opening dist folder in Explorer...
explorer /select,"%OUT_INSTALLER%"
endlocal
exit /b 0

:iscc_missing
echo.
echo ERROR: Inno Setup compiler ^(ISCC.exe^) not found or path is invalid.
echo Install Inno Setup 6 from https://jrsoftware.org/isinfo.php then re-run this script.
echo Or set IP_ISCC to the full path of ISCC.exe.
pause
exit /b 1
