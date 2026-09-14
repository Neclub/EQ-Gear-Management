@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Publish a locally built EQGM-x.y.z.exe as a GitHub Release.
REM Chat "Publish new build" first updates version + docs and pushes to GitHub,
REM then runs this script. Do not build the exe before that source is on origin.
REM Pushing main no longer builds the exe on GitHub Actions.

where gh >nul 2>&1
if errorlevel 1 (
  echo ERROR: GitHub CLI ^(gh^) is not on PATH. Install it and run gh auth login.
  exit /b 1
)

git diff --quiet --exit-code
if errorlevel 1 (
  echo ERROR: Uncommitted changes. Commit the version bump first, then publish.
  exit /b 1
)
git diff --cached --quiet --exit-code
if errorlevel 1 (
  echo ERROR: Staged but uncommitted changes. Commit first, then publish.
  exit /b 1
)

git status -sb | findstr /C:"ahead" >nul
if not errorlevel 1 (
  echo Pushing commits to origin so the release tag matches GitHub...
  git push origin HEAD
  if errorlevel 1 (
    echo ERROR: git push failed.
    exit /b 1
  )
)

echo.
echo Building local executable...
call "%~dp0build_exe.bat"
if errorlevel 1 (
  echo ERROR: Local build failed.
  exit /b 1
)

for /f "delims=" %%V in ('py "%~dp0scripts\print_package_version.py"') do set "IP_VER=%%V"
set "OUT_EXE=%~dp0dist\EQGM-%IP_VER%.exe"
if not exist "%OUT_EXE%" (
  echo ERROR: Expected exe was not created:
  echo   %OUT_EXE%
  exit /b 1
)

gh release view "v%IP_VER%" >nul 2>&1
if not errorlevel 1 (
  echo ERROR: GitHub Release v%IP_VER% already exists.
  exit /b 1
)

echo.
echo Creating GitHub Release v%IP_VER% from local exe...
gh release create "v%IP_VER%" "%OUT_EXE%" --title "EQ Gear Management %IP_VER%" --generate-notes --latest
if errorlevel 1 (
  echo ERROR: gh release create failed.
  exit /b 1
)

echo.
echo Published https://github.com/Neclub/EQ-Gear-Management/releases/tag/v%IP_VER%
endlocal
exit /b 0
