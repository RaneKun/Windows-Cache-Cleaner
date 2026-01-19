"""
Windows Cache Cleaner - Build to EXE Script (Python version)
This script compiles the Python script to a standalone .exe file using PyInstaller
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def print_info(text):
    """Print an info message"""
    print(f"[INFO] {text}")

def print_success(text):
    """Print a success message"""
    print(f"[SUCCESS] {text}")

def print_error(text):
    """Print an error message"""
    print(f"[ERROR] {text}")

def print_warning(text):
    """Print a warning message"""
    print(f"[WARNING] {text}")

def check_python():
    """Check if Python is installed"""
    try:
        version = sys.version.split()[0]
        print_info(f"Python {version} detected")
        return True
    except:
        print_error("Python not found!")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print_info("PyInstaller already installed")
        return True
    except ImportError:
        print_info("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print_success("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install PyInstaller!")
            return False

def check_files():
    """Check if required files exist"""
    script_file = "windows_cache_cleaner_IMPROVED.py"
    icon_file = "windows_cache_cleaner.ico"
    
    if not os.path.exists(script_file):
        print_error(f"{script_file} not found in current directory!")
        return False, None
    
    print_info(f"Script file found: {script_file}")
    
    if not os.path.exists(icon_file):
        print_warning(f"Icon file '{icon_file}' not found!")
        print_warning("The EXE will be created without a custom icon.")
        return True, None
    
    print_info(f"Icon file found: {icon_file}")
    return True, icon_file

def cleanup_old_builds():
    """Remove old build artifacts"""
    print_info("Cleaning up old build files...")
    
    directories_to_remove = ["build", "dist"]
    files_to_remove = ["windows_cache_cleaner_IMPROVED.spec"]
    
    for directory in directories_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    
    print_info("Cleanup complete")

def build_exe(icon_file):
    """Build the executable using PyInstaller"""
    print_header("Starting PyInstaller build process...")
    print("This may take a few minutes...\n")
    
    # Build PyInstaller command
    command = [
        "pyinstaller",
        "--onefile",                          # Single executable file
        "--windowed",                         # No console window
        "--name", "Windows Cache Cleaner",   # Name of the executable
        "--clean",                            # Clean PyInstaller cache
        "--noconfirm",                        # Replace output directory without asking
    ]
    
    # Add icon if available
    if icon_file:
        command.extend(["--icon", icon_file])
        command.extend(["--add-data", f"{icon_file};."])
    
    # Add the script to compile
    command.append("windows_cache_cleaner_IMPROVED.py")
    
    # Execute PyInstaller
    try:
        result = subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Build failed with error code {e.returncode}")
        return False

def cleanup_build_artifacts():
    """Remove build artifacts but keep dist folder"""
    print_info("Cleaning up build artifacts...")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    if os.path.exists("windows_cache_cleaner_IMPROVED.spec"):
        os.remove("windows_cache_cleaner_IMPROVED.spec")
    
    print_info("Cleanup complete")

def main():
    """Main build process"""
    print_header("Windows Cache Cleaner - Build to EXE")
    
    # Step 1: Check Python
    if not check_python():
        return False
    
    print()
    
    # Step 2: Check/Install PyInstaller
    if not check_pyinstaller():
        return False
    
    print()
    
    # Step 3: Check required files
    files_ok, icon_file = check_files()
    if not files_ok:
        return False
    
    print()
    
    # Step 4: Cleanup old builds
    cleanup_old_builds()
    
    print()
    
    # Step 5: Build the executable
    if not build_exe(icon_file):
        print_header("Build Failed!")
        print("Please check the error messages above.\n")
        return False
    
    print()
    
    # Step 6: Cleanup build artifacts
    cleanup_build_artifacts()
    
    print()
    
    # Success!
    print_header("Build completed successfully!")
    
    print("The executable has been created in the 'dist' folder:")
    print("  dist\\Windows Cache Cleaner.exe\n")
    
    print("You can now:")
    print("  1. Run the .exe file to test it")
    print("  2. Move it to any location you want")
    print("  3. Create a desktop shortcut")
    print("  4. Share it with others (they don't need Python!)\n")
    
    print_header("Build process finished!")
    
    return True

if __name__ == "__main__":
    success = main()
    
    # Pause before exit (like the batch file)
    input("\nPress Enter to exit...")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
