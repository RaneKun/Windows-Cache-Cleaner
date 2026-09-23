@echo off
REM ============================================================================
REM Windows Cache Cleaner - Build to EXE Script (Hardened)
REM
REM Changes vs. the original:
REM   - Enforces Python 3.10+ (matches the README requirement)
REM   - Checks that pip is actually available before trying to use it
REM   - Uses "python -m pip" instead of bare "pip" so the pip that runs is
REM     guaranteed to belong to the same Python that "python" resolves to
REM   - Only checks the network when PyInstaller is actually missing (i.e.
REM     when an install is genuinely needed), with a clearer error if offline
REM   - pushd's into the script's own folder, so double-clicking from
REM     anywhere works the same as running it from inside the folder
REM   - Verifies the .exe was really created before trying to move it, and
REM     verifies it really landed at the destination after moving
REM
REM After a successful build:
REM   - The finished .exe is moved to the same folder as this script
REM   - The dist\ folder, build\ folder, and .spec file are all removed
REM   - Nothing but the .exe (and your source files) is left behind
REM ============================================================================

setlocal enabledelayedexpansion

REM Work from the script's own folder, no matter where it was invoked from
pushd "%~dp0"

echo.
echo ========================================
echo Windows Cache Cleaner - Build to EXE
echo ========================================
echo.

REM ----------------------------------------------------------------------------
REM 1. Python presence and version check
REM ----------------------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed, or not on PATH.
    echo.
    echo         Install Python 3.10 or newer from https://www.python.org/
    echo         During installation, make sure "Add Python to PATH" is checked.
    echo.
    popd
    pause
    exit /b 1
)

REM Parse "Python 3.11.5" into major/minor. --version writes to stdout on
REM Python 3.4+, but we redirect stderr to stdout anyway for maximum safety.
set "PYVER="
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYVER=%%v"

if not defined PYVER (
    echo [ERROR] Could not determine the installed Python version.
    echo         "python --version" returned no parsable output.
    echo.
    popd
    pause
    exit /b 1
)

set "PYMAJOR="
set "PYMINOR="
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set "PYMAJOR=%%a"
    set "PYMINOR=%%b"
)

REM Defensive: make sure we actually got two numbers out of it
echo !PYMAJOR!| findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo [ERROR] Could not parse Python version from: !PYVER!
    echo.
    popd
    pause
    exit /b 1
)

set "PYVER_OK=0"
if !PYMAJOR! GTR 3 set "PYVER_OK=1"
if !PYMAJOR! EQU 3 if !PYMINOR! GEQ 10 set "PYVER_OK=1"

if "!PYVER_OK!"=="0" (
    echo [ERROR] Python !PYMAJOR!.!PYMINOR! detected, but Python 3.10+ is required.
    echo.
    echo         Upgrade Python from https://www.python.org/ and re-run this script.
    echo.
    popd
    pause
    exit /b 1
)

echo [INFO] Python !PYMAJOR!.!PYMINOR! detected (meets 3.10+ requirement)
echo.

REM ----------------------------------------------------------------------------
REM 2. pip availability check
REM ----------------------------------------------------------------------------
REM Using "python -m pip" (not bare "pip") guarantees we're talking to the pip
REM that ships with the same Python interpreter "python" resolves to. On systems
REM with multiple Python installs, bare "pip" can silently target a different
REM interpreter and install packages the build will never see.
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available for this Python installation.
    echo.
    echo         Reinstall Python and make sure "pip" is included, or run:
    echo             python -m ensurepip --upgrade
    echo.
    popd
    pause
    exit /b 1
)
echo [INFO] pip is available
echo.

REM ----------------------------------------------------------------------------
REM 3. PyInstaller check (with on-demand internet check + auto-install)
REM ----------------------------------------------------------------------------
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Checking network connection...
    echo.

    REM Only bother checking the network when we actually need to install
    REM something. Ping pypi.org (the index pip would pull from) with a short
    REM timeout, and treat any failure as "we can't install right now".
    ping -n 1 -w 2000 pypi.org >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Cannot reach pypi.org to install PyInstaller.
        echo.
        echo         Either:
        echo           1. Connect to the internet and re-run this script, or
        echo           2. Install PyInstaller manually and re-run:
        echo                  python -m pip install pyinstaller
        echo.
        popd
        pause
        exit /b 1
    )

    echo [INFO] Installing PyInstaller...
    echo.
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install PyInstaller.
        echo         Check the pip output above for details.
        echo.
        popd
        pause
        exit /b 1
    )

    REM Re-verify the import actually succeeded, in case pip reported success
    REM but the package still isn't importable for some reason.
    python -c "import PyInstaller" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo [ERROR] PyInstaller installed, but still can't be imported.
        echo         Your Python environment may be misconfigured.
        echo.
        popd
        pause
        exit /b 1
    )

    echo.
    echo [SUCCESS] PyInstaller installed successfully
    echo.
) else (
    echo [INFO] PyInstaller already installed
    echo.
)

REM ----------------------------------------------------------------------------
REM 4. Source file presence check
REM ----------------------------------------------------------------------------
if not exist "windows_cache_cleaner.py" (
    echo [ERROR] windows_cache_cleaner.py not found in this folder:
    echo         %~dp0
    echo.
    echo         Make sure the script is in the same folder as this batch file.
    echo.
    popd
    pause
    exit /b 1
)
echo [INFO] Script file found: windows_cache_cleaner.py
echo.

REM ----------------------------------------------------------------------------
REM 5. Icon file check (warning only - build still works without it)
REM ----------------------------------------------------------------------------
if not exist "windows_cache_cleaner.ico" (
    echo [WARNING] Icon file 'windows_cache_cleaner.ico' not found.
    echo           The EXE will be built without a custom icon.
    echo.
    set "ICON_PARAM="
) else (
    echo [INFO] Icon file found: windows_cache_cleaner.ico
    echo.
    set "ICON_PARAM=--icon=windows_cache_cleaner.ico"
)

REM ----------------------------------------------------------------------------
REM 6. Clean up any leftovers from a previous build
REM ----------------------------------------------------------------------------
echo [INFO] Cleaning up old build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Windows Cache Cleaner.spec" del /q "Windows Cache Cleaner.spec"
echo [INFO] Cleanup complete
echo.

REM ----------------------------------------------------------------------------
REM 7. Build
REM ----------------------------------------------------------------------------
echo ========================================
echo Starting PyInstaller build process...
echo ========================================
echo.
echo This may take a few minutes...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Windows Cache Cleaner" ^
    %ICON_PARAM% ^
    --add-data "windows_cache_cleaner.ico;." ^
    --clean ^
    --noconfirm ^
    windows_cache_cleaner.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Build failed!
    echo ========================================
    echo.
    echo Check the PyInstaller output above for details.
    echo.
    popd
    pause
    exit /b 1
)

REM ----------------------------------------------------------------------------
REM 8. Verify the .exe really exists before trying to move it
REM ----------------------------------------------------------------------------
if not exist "dist\Windows Cache Cleaner.exe" (
    echo.
    echo ========================================
    echo [ERROR] Build reported success, but the .exe was not found at:
    echo         dist\Windows Cache Cleaner.exe
    echo ========================================
    echo.
    popd
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Build completed successfully!
echo ========================================
echo.

REM ----------------------------------------------------------------------------
REM 9. Move the .exe up to the script folder
REM ----------------------------------------------------------------------------
echo [INFO] Moving executable to script folder...
if exist "Windows Cache Cleaner.exe" (
    REM A previous copy is sitting here - if it's still running, the move will
    REM fail with a sharing violation rather than a clear message, so warn now.
    echo [WARNING] An existing "Windows Cache Cleaner.exe" was found here.
    echo           If it's currently running, close it first.
    echo.
    del /q "Windows Cache Cleaner.exe" >nul 2>&1
)

move /Y "dist\Windows Cache Cleaner.exe" "%~dp0Windows Cache Cleaner.exe" >nul
if errorlevel 1 (
    echo [ERROR] Failed to move the executable into the script folder.
    echo.
    echo         It's still available at:
    echo             %~dp0dist\Windows Cache Cleaner.exe
    echo         You can move it manually.
    echo.
    popd
    pause
    exit /b 1
)

REM Verify it actually landed
if not exist "%~dp0Windows Cache Cleaner.exe" (
    echo [ERROR] Move reported success, but the .exe isn't at the destination.
    echo.
    popd
    pause
    exit /b 1
)

echo [INFO] Executable moved to:
echo        %~dp0Windows Cache Cleaner.exe
echo.

REM ----------------------------------------------------------------------------
REM 10. Clean up every remaining build artifact
REM ----------------------------------------------------------------------------
echo [INFO] Cleaning up build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Windows Cache Cleaner.spec" del /q "Windows Cache Cleaner.spec"
echo [INFO] Cleanup complete
echo.

REM ----------------------------------------------------------------------------
REM Done
REM ----------------------------------------------------------------------------
echo ========================================
echo Build process finished!
echo ========================================
echo.
echo The executable is ready in this folder:
echo   %~dp0Windows Cache Cleaner.exe
echo.
echo You can now:
echo   1. Run the .exe file to test it
echo   2. Move it to any location you want
echo   3. Create a desktop shortcut
echo.

popd
pause
