@echo off
REM ============================================================================
REM Windows Cache Cleaner - Build to EXE Script
REM This script compiles the Python script to a standalone .exe file
REM ============================================================================

echo.
echo ========================================
echo Windows Cache Cleaner - Build to EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python detected successfully
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing PyInstaller...
    echo.
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
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

REM Check if the Python script exists
if not exist "windows_cache_cleaner_IMPROVED.py" (
    echo [ERROR] windows_cache_cleaner_IMPROVED.py not found in current directory!
    echo Please make sure the script is in the same folder as this batch file.
    pause
    exit /b 1
)

echo [INFO] Script file found: windows_cache_cleaner_IMPROVED.py
echo.

REM Check if icon file exists
if not exist "windows_cache_cleaner.ico" (
    echo [WARNING] Icon file 'windows_cache_cleaner.ico' not found!
    echo The EXE will be created without a custom icon.
    echo.
    set ICON_PARAM=
) else (
    echo [INFO] Icon file found: windows_cache_cleaner.ico
    echo.
    set ICON_PARAM=--icon=windows_cache_cleaner.ico
)

REM Clean up old build files
echo [INFO] Cleaning up old build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "windows_cache_cleaner_IMPROVED.spec" del /q "windows_cache_cleaner_IMPROVED.spec"
echo [INFO] Cleanup complete
echo.

REM Build the executable
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
    windows_cache_cleaner_IMPROVED.py

REM Check if build was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Build completed successfully!
echo ========================================
echo.
echo The executable has been created in the 'dist' folder:
echo   dist\Windows Cache Cleaner.exe
echo.
echo You can now:
echo   1. Run the .exe file to test it
echo   2. Move it to any location you want
echo   3. Create a desktop shortcut
echo.

REM Clean up build artifacts (optional)
echo [INFO] Cleaning up build artifacts...
if exist "build" rmdir /s /q "build"
if exist "windows_cache_cleaner_IMPROVED.spec" del /q "windows_cache_cleaner_IMPROVED.spec"
echo [INFO] Cleanup complete
echo.

echo ========================================
echo Build process finished!
echo ========================================
echo.
pause
