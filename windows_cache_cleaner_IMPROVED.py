# Import necessary modules for the application
import os  # Provides operating system dependent functionality
import shutil  # Provides high-level file operations
import json  # Provides JSON parsing and serialization
import glob  # Provides pathname pattern expansion
import subprocess  # Allows running external commands
import datetime  # Provides date and time functionality
import time  # Provides time-related functions
import winreg  # Provides Windows Registry access
import ctypes  # Provides Windows API access
import sys  # Provides system-specific parameters and functions
from pathlib import Path  # Provides object-oriented filesystem paths

# Import PyQt6 components for creating the GUI
from PyQt6.QtWidgets import (
    QApplication,  # Manages application control flow and main settings
    QWidget,  # Base class for all UI objects
    QVBoxLayout,  # Lines up widgets vertically
    QHBoxLayout,  # Lines up widgets horizontally
    QCheckBox,  # Creates toggleable checkboxes
    QPushButton,  # Creates clickable buttons
    QLabel,  # Displays text or images
    QMessageBox,  # Provides dialog boxes for messages
    QGridLayout,  # Organizes widgets in a grid
    QProgressBar,  # Shows progress of an operation
    QTextEdit  # Provides multi-line text display
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal  # Core Qt functionality, threading, and signals
from PyQt6.QtGui import QPixmap, QIcon, QFont  # GUI elements for images, icons, and fonts

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# File paths for configuration and logging
APP_NAME = "Windows Cache Cleaner"  # Application name
APP_VERSION = "2.0"  # Application version
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA")) / "WindowsCacheCleaner"  # App data directory
CONFIG_PATH = APP_DATA_DIR / "config.json"  # Configuration file path
LOG_DIR = APP_DATA_DIR / "logs"  # Log directory path

# UI Layout constants
MAX_ROWS_PER_COLUMN = 6  # Maximum number of checkbox rows per column
HOVER_DARKNESS_FACTOR = 0.8  # How much darker the hover color should be (20% darker)
PRESSED_DARKNESS_FACTOR = 0.6  # How much darker the pressed color should be (40% darker)

# Cleanup operation constants
BATCH_DELETE_SIZE = 100  # Number of files to delete before updating progress

# =============================================================================
# ADMIN PRIVILEGES CHECK
# =============================================================================

def is_admin():
    """
    Check if the script is running with administrator privileges.
    
    Returns:
        bool: True if running as admin, False otherwise
    """
    try:
        # Use Windows API to check admin status
        result = ctypes.windll.shell32.IsUserAnAdmin()
        return result
    except Exception as e:
        # If check fails, assume not admin
        return False

# =============================================================================
# ACCENT COLOR DETECTION
# =============================================================================

def get_windows_accent_color():
    """
    Get the Windows accent color from the registry.
    
    Returns:
        str: Hex color code (e.g., "#0078d4")
    """
    try:
        # Open registry key for Windows personalization settings
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\DWM") as key:
            # Read accent color value
            accent_color, _ = winreg.QueryValueEx(key, "AccentColor")
            
            # Convert from ABGR integer to RGB hex
            # Windows stores color as ABGR (Alpha-Blue-Green-Red)
            blue = (accent_color >> 16) & 0xFF  # Extract blue component
            green = (accent_color >> 8) & 0xFF  # Extract green component
            red = accent_color & 0xFF  # Extract red component
            
            # Format as hex color code
            color_hex = f"#{red:02x}{green:02x}{blue:02x}"
            return color_hex
    except Exception:
        # Fallback to default Windows blue if registry access fails
        return "#0078d4"

def get_darker_color(hex_color, factor=0.8):
    """
    Create a darker version of a color for hover/pressed states.
    
    Args:
        hex_color (str): Hex color code (e.g., "#0078d4")
        factor (float): Darkness factor (0.0-1.0, where 1.0 is original color)
        
    Returns:
        str: Darker hex color code
    """
    # Remove '#' prefix if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB integers
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Apply darkness factor
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    
    # Convert back to hex
    darker_color = f"#{r:02x}{g:02x}{b:02x}"
    return darker_color

# =============================================================================
# LOGGING SYSTEM
# =============================================================================

def ensure_log_dir():
    """
    Create the log directory if it doesn't exist.
    Also creates the app data directory if needed.
    """
    # Create app data directory
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def generate_log_filename():
    """
    Generate a timestamped log filename.
    
    Returns:
        Path: Full path to the log file
    """
    # Format: cleanup_log_YYYY-MM-DD_HH-MM.txt
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = LOG_DIR / f"cleanup_log_{timestamp}.txt"
    return filename

def write_log_header(log_file, start_time):
    """
    Write the header section of the log file.
    
    Args:
        log_file: File object to write to
        start_time: Start time of the cleanup operation
    """
    log_file.write("=" * 60 + "\n")
    log_file.write(f"{APP_NAME} - CLEANUP REPORT\n")
    log_file.write(f"Version {APP_VERSION}\n")
    log_file.write("=" * 60 + "\n")
    log_file.write(f"Cleanup performed on: {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}\n")
    log_file.write("-" * 60 + "\n\n")

def write_log_footer(log_file, start_time, end_time, operations_count, 
                     success_count, failed_count, total_size_freed):
    """
    Write the footer section of the log file with summary statistics.
    
    Args:
        log_file: File object to write to
        start_time: Start time of cleanup
        end_time: End time of cleanup
        operations_count: Number of operations performed
        success_count: Number of successful file operations
        failed_count: Number of failed file operations
        total_size_freed: Total bytes freed
    """
    duration = end_time - start_time
    
    log_file.write("\n" + "=" * 60 + "\n")
    log_file.write("CLEANUP SUMMARY\n")
    log_file.write("=" * 60 + "\n")
    log_file.write(f"Total operations performed: {operations_count}\n")
    log_file.write(f"Successful file operations: {success_count}\n")
    log_file.write(f"Failed file operations: {failed_count}\n")
    log_file.write(f"Space freed: {format_size(total_size_freed)}\n")
    log_file.write(f"Total time taken: {duration:.2f} seconds\n")
    log_file.write(f"Cleanup completed at: {datetime.datetime.now().strftime('%H:%M')}\n")
    log_file.write("=" * 60 + "\n")

def log_success(log_file, message):
    """
    Write a formatted success message to the log.
    
    Args:
        log_file: File object to write to
        message: Success message to log
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{timestamp}] [SUCCESS] {message}\n")

def log_failure(log_file, message, error):
    """
    Write a formatted failure message to the log with error details.
    
    Args:
        log_file: File object to write to
        message: Failure message to log
        error: Error details
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{timestamp}] [FAILED] {message}\n")
    log_file.write(f"         Reason: {error}\n")

def log_info(log_file, message):
    """
    Write a formatted info message to the log.
    
    Args:
        log_file: File object to write to
        message: Info message to log
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{timestamp}] [INFO] {message}\n")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_size(bytes_size):
    """
    Format a byte size into a human-readable string.
    
    Args:
        bytes_size (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "4.2 GB", "150 MB")
    """
    # Convert bytes to appropriate unit
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def get_folder_size(path):
    """
    Calculate the total size of all files in a folder.
    
    Args:
        path (str): Path to the folder
        
    Returns:
        tuple: (total_size_bytes, file_count)
    """
    total_size = 0
    file_count = 0
    
    # Check if path exists
    if not os.path.exists(path):
        return 0, 0
    
    try:
        # Walk through directory tree
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    # Add file size to total
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except (OSError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
    except (OSError, PermissionError):
        # Skip directories that can't be accessed
        pass
    
    return total_size, file_count

# =============================================================================
# CONFIGURATION HANDLING
# =============================================================================

def load_config():
    """
    Load configuration from JSON file.
    
    Returns:
        dict: Configuration dictionary with checkbox states
    """
    # Check if config file exists
    if not CONFIG_PATH.exists():
        return {}
    
    try:
        # Read and parse JSON config
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Return empty dict if config is corrupt or unreadable
        return {}

def save_config(cfg):
    """
    Save configuration to JSON file.
    
    Args:
        cfg (dict): Configuration dictionary to save
    """
    # Ensure directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write config to file
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

# =============================================================================
# CLEANUP WORKER THREAD
# =============================================================================

class CleanupWorker(QThread):
    """
    Worker thread for performing cleanup operations in the background.
    This prevents the UI from freezing during cleanup.
    """
    
    # Define signals for communication with the main thread
    progress_updated = pyqtSignal(int)  # Emits progress percentage (0-100)
    status_updated = pyqtSignal(str)  # Emits status messages
    operation_started = pyqtSignal(str)  # Emits when an operation starts
    operation_completed = pyqtSignal(str, int, int, int)  # Emits (name, success, failed, bytes)
    task_completed = pyqtSignal(int, int, int, float)  # Emits (ops, success, failed, size_freed, duration)
    error_occurred = pyqtSignal(str)  # Emits error messages
    
    def __init__(self, selected_operations, log_file_path):
        """
        Initialize the cleanup worker thread.
        
        Args:
            selected_operations (dict): Dictionary of operation_name -> cleanup_function
            log_file_path (Path): Path to the log file
        """
        super().__init__()
        self.selected_operations = selected_operations  # Operations to perform
        self.log_file_path = log_file_path  # Log file path
        self.is_running = True  # Flag to control thread execution
        self.current_operation = ""  # Name of current operation
        
    def run(self):
        """
        Main method that runs when the thread starts.
        Performs all selected cleanup operations.
        """
        start_time = time.time()
        
        # Initialize counters
        operations_count = 0
        total_success_count = 0
        total_failed_count = 0
        total_size_freed = 0
        
        # Open log file for writing
        with open(self.log_file_path, 'w', encoding='utf-8') as log_file:
            # Write log header
            write_log_header(log_file, start_time)
            
            # Log selected operations
            operation_names = list(self.selected_operations.keys())
            log_info(log_file, f"Selected operations: {', '.join(operation_names)}")
            log_file.write("\n")
            
            # Calculate total operations for progress tracking
            total_operations = len(self.selected_operations)
            
            # Execute each operation
            for idx, (operation_name, operation_func) in enumerate(self.selected_operations.items()):
                # Check if thread should stop
                if not self.is_running:
                    log_info(log_file, "Cleanup cancelled by user")
                    break
                
                # Update current operation
                self.current_operation = operation_name
                self.operation_started.emit(operation_name)
                log_info(log_file, f"Starting operation: {operation_name}")
                
                # Calculate progress percentage
                progress = int((idx / total_operations) * 100)
                self.progress_updated.emit(progress)
                
                # Execute the cleanup operation
                try:
                    success_count, failed_count, bytes_freed = operation_func(log_file, self)
                    
                    # Update totals
                    operations_count += 1
                    total_success_count += success_count
                    total_failed_count += failed_count
                    total_size_freed += bytes_freed
                    
                    # Log completion
                    log_info(log_file, f"Completed operation: {operation_name} - "
                                      f"Success: {success_count}, Failed: {failed_count}, "
                                      f"Freed: {format_size(bytes_freed)}")
                    
                    # Emit completion signal
                    self.operation_completed.emit(operation_name, success_count, 
                                                 failed_count, bytes_freed)
                    
                except Exception as e:
                    # Log unexpected errors
                    log_failure(log_file, f"Operation: {operation_name}", str(e))
                    total_failed_count += 1
                    self.error_occurred.emit(f"Error in {operation_name}: {str(e)}")
                
                log_file.write("\n")
            
            # Set progress to 100%
            self.progress_updated.emit(100)
            
            # Calculate total duration
            end_time = time.time()
            duration = end_time - start_time
            
            # Write log footer
            write_log_footer(log_file, start_time, end_time, operations_count,
                           total_success_count, total_failed_count, total_size_freed)
        
        # Emit completion signal with statistics
        self.task_completed.emit(operations_count, total_success_count, 
                                total_failed_count, total_size_freed)
    
    def stop(self):
        """
        Stop the worker thread gracefully.
        """
        self.is_running = False

# =============================================================================
# CORE CLEANUP FUNCTIONS
# =============================================================================

def delete_folder_contents(path, log_file, worker):
    """
    Recursively delete all files and subdirectories in a folder.
    This is the main workhorse function used by most cleanup operations.
    
    Args:
        path (str): Path to the folder to clean
        log_file: File object for logging
        worker: Worker thread object for progress updates
        
    Returns:
        tuple: (success_count, failed_count, bytes_freed)
    """
    # Initialize counters
    success_count = 0
    failed_count = 0
    bytes_freed = 0
    
    # Check if path exists
    if not os.path.exists(path):
        log_info(log_file, f"Path does not exist, skipping: {path}")
        return 0, 0, 0
    
    log_info(log_file, f"Starting to clean folder: {path}")
    
    try:
        # Walk through directory tree
        for root, dirs, files in os.walk(path, topdown=False):
            # Check if worker should stop
            if not worker.is_running:
                break
            
            # Delete all files in current directory
            for filename in files:
                # Check if worker should stop
                if not worker.is_running:
                    break
                
                filepath = os.path.join(root, filename)
                
                try:
                    # Get file size before deletion
                    file_size = os.path.getsize(filepath)
                    
                    # Delete the file
                    os.remove(filepath)
                    
                    # Update counters
                    success_count += 1
                    bytes_freed += file_size
                    
                    # Update status every 10 files to reduce UI updates
                    if success_count % 10 == 0:
                        worker.status_updated.emit(
                            f"{worker.current_operation}: Deleted {success_count} files "
                            f"({format_size(bytes_freed)} freed)"
                        )
                    
                except (PermissionError, FileNotFoundError, OSError) as e:
                    # Log failure for specific file errors
                    failed_count += 1
                    log_failure(log_file, f"Delete file: {filepath}", str(e))
                    
                except Exception as e:
                    # Log unexpected errors (should investigate these)
                    failed_count += 1
                    log_failure(log_file, f"Unexpected error deleting file: {filepath}", str(e))
            
            # Delete all subdirectories in current directory
            for dirname in dirs:
                # Check if worker should stop
                if not worker.is_running:
                    break
                
                dirpath = os.path.join(root, dirname)
                
                try:
                    # Delete directory and all its contents
                    shutil.rmtree(dirpath, ignore_errors=True)
                    success_count += 1
                    
                except Exception as e:
                    # Log failure
                    failed_count += 1
                    log_failure(log_file, f"Delete directory: {dirpath}", str(e))
    
    except Exception as e:
        # Log unexpected errors during walk
        log_failure(log_file, f"Error walking directory: {path}", str(e))
    
    # Log final statistics
    log_info(log_file, f"Folder cleanup completed - Success: {success_count}, "
                      f"Failed: {failed_count}, Freed: {format_size(bytes_freed)}")
    
    return success_count, failed_count, bytes_freed

def generic_folder_cleanup(operation_name, path, log_file, worker):
    """
    Generic cleanup function for folder-based operations.
    This reduces code duplication across similar cleanup functions.
    
    Args:
        operation_name (str): Name of the operation for logging
        path (str): Path to clean
        log_file: File object for logging
        worker: Worker thread object
        
    Returns:
        tuple: (success_count, failed_count, bytes_freed)
    """
    log_info(log_file, f"Starting {operation_name}...")
    worker.status_updated.emit(f"Cleaning: {operation_name}")
    
    success, failed, freed = delete_folder_contents(path, log_file, worker)
    
    log_info(log_file, f"{operation_name} completed - Success: {success}, "
                      f"Failed: {failed}, Freed: {format_size(freed)}")
    
    return success, failed, freed

# Individual cleanup functions
# Each function follows the same pattern: name, path, log_file, worker

def cleanup_windows_temp(log_file, worker):
    r"""
    Clean Windows system temporary files.
    Location: C:\Windows\Temp
    """
    return generic_folder_cleanup(
        "Windows Temp Files",
        r"C:\Windows\Temp",
        log_file,
        worker
    )

def cleanup_user_temp(log_file, worker):
    r"""
    Clean user temporary files.
    Location: %LOCALAPPDATA%\Temp
    """
    path = str(Path(os.getenv("LOCALAPPDATA")) / "Temp")
    return generic_folder_cleanup(
        "User Temp Files",
        path,
        log_file,
        worker
    )

def cleanup_prefetch(log_file, worker):
    r"""
    Clean Windows Prefetch files.
    Location: C:\Windows\Prefetch
    """
    return generic_folder_cleanup(
        "Prefetch Files",
        r"C:\Windows\Prefetch",
        log_file,
        worker
    )

def cleanup_windows_update(log_file, worker):
    r"""
    Clean Windows Update download cache.
    Location: C:\Windows\SoftwareDistribution\Download
    """
    return generic_folder_cleanup(
        "Windows Update Remnants",
        r"C:\Windows\SoftwareDistribution\Download",
        log_file,
        worker
    )

def cleanup_delivery_opt(log_file, worker):
    r"""
    Clean Delivery Optimization cache.
    Location: C:\ProgramData\Microsoft\Windows\DeliveryOptimization
    """
    return generic_folder_cleanup(
        "Delivery Optimization Cache",
        r"C:\ProgramData\Microsoft\Windows\DeliveryOptimization",
        log_file,
        worker
    )

def cleanup_explorer_cache(log_file, worker):
    r"""
    Clean Windows Explorer cache (icons, thumbnails).
    Location: %LOCALAPPDATA%\Microsoft\Windows\Explorer
    """
    path = str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "Explorer")
    return generic_folder_cleanup(
        "Explorer Icon + Thumbnail Cache",
        path,
        log_file,
        worker
    )

def cleanup_gpu_cache(log_file, worker):
    r"""
    Clean GPU shader caches for NVIDIA and AMD.
    Locations: 
        - %LOCALAPPDATA%\NVIDIA\DXCache
        - %LOCALAPPDATA%\NVIDIA\GLCache
        - %LOCALAPPDATA%\AMD\DxCache
    """
    log_info(log_file, "Starting GPU Cache cleanup...")
    worker.status_updated.emit("Cleaning: GPU Shader Cache")
    
    base = Path(os.getenv("LOCALAPPDATA"))
    targets = [
        base / "NVIDIA" / "DXCache",
        base / "NVIDIA" / "GLCache",
        base / "AMD" / "DxCache",
    ]
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    for target_path in targets:
        if not worker.is_running:
            break
        success, failed, freed = delete_folder_contents(str(target_path), log_file, worker)
        total_success += success
        total_failed += failed
        total_freed += freed
    
    log_info(log_file, f"GPU Cache cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_store_cache(log_file, worker):
    r"""
    Clean Microsoft Store and UWP app caches.
    Location: %LOCALAPPDATA%\Packages\*\LocalCache, TempState, AC
    """
    log_info(log_file, "Starting Store and UWP cache cleanup...")
    worker.status_updated.emit("Cleaning: Windows Store + UWP Cache")
    
    base = Path(os.getenv("LOCALAPPDATA")) / "Packages"
    
    if not base.exists():
        log_info(log_file, "Packages directory not found, skipping")
        return 0, 0, 0
    
    all_packages = [p for p in base.iterdir() if p.is_dir()]
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    for folder in all_packages:
        if not worker.is_running:
            break
        
        for cache_dir in ["TempState", "AC", "LocalCache"]:
            if not worker.is_running:
                break
            
            cache_path = folder / cache_dir
            success, failed, freed = delete_folder_contents(str(cache_path), log_file, worker)
            total_success += success
            total_failed += failed
            total_freed += freed
    
    log_info(log_file, f"Store and UWP cache cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_crash_dumps(log_file, worker):
    r"""
    Clean system and application crash dump files.
    Locations:
        - C:\Windows\Minidump (system crashes)
        - %LOCALAPPDATA%\CrashDumps (application crashes)
    """
    log_info(log_file, "Starting crash dump cleanup...")
    worker.status_updated.emit("Cleaning: Crash Dumps")
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    # System minidumps
    system_dumps = r"C:\Windows\Minidump"
    success, failed, freed = delete_folder_contents(system_dumps, log_file, worker)
    total_success += success
    total_failed += failed
    total_freed += freed
    
    # Check if worker should stop
    if not worker.is_running:
        return total_success, total_failed, total_freed
    
    # Application crash dumps
    app_dumps = str(Path(os.getenv("LOCALAPPDATA")) / "CrashDumps")
    success, failed, freed = delete_folder_contents(app_dumps, log_file, worker)
    total_success += success
    total_failed += failed
    total_freed += freed
    
    log_info(log_file, f"Crash dump cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_wer_logs(log_file, worker):
    r"""
    Clean Windows Error Reporting logs.
    Location: C:\ProgramData\Microsoft\Windows\WER
    """
    return generic_folder_cleanup(
        "WER Logs",
        r"C:\ProgramData\Microsoft\Windows\WER",
        log_file,
        worker
    )

def cleanup_d3d_cache(log_file, worker):
    r"""
    Clean DirectX D3D shader cache.
    Location: %USERPROFILE%\AppData\Local\D3DSCache
    """
    path = str(Path.home() / "AppData" / "Local" / "D3DSCache")
    return generic_folder_cleanup(
        "DirectX Shader Cache",
        path,
        log_file,
        worker
    )

def cleanup_windows_logs(log_file, worker):
    r"""
    Clean Windows system logs.
    Locations:
        - C:\Windows\Logs
        - C:\Windows\System32\LogFiles
    """
    log_info(log_file, "Starting Windows logs cleanup...")
    worker.status_updated.emit("Cleaning: Windows Logs")
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    # Windows logs directory
    logs_path1 = r"C:\Windows\Logs"
    success, failed, freed = delete_folder_contents(logs_path1, log_file, worker)
    total_success += success
    total_failed += failed
    total_freed += freed
    
    # Check if worker should stop
    if not worker.is_running:
        return total_success, total_failed, total_freed
    
    # System32 log files
    logs_path2 = r"C:\Windows\System32\LogFiles"
    success, failed, freed = delete_folder_contents(logs_path2, log_file, worker)
    total_success += success
    total_failed += failed
    total_freed += freed
    
    log_info(log_file, f"Windows logs cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_onedrive_photos(log_file, worker):
    r"""
    Clean OneDrive and Photos app caches.
    Locations:
        - %LOCALAPPDATA%\Microsoft\OneDrive
        - %LOCALAPPDATA%\Packages\Microsoft.Windows.Photos_*\LocalCache
    """
    log_info(log_file, "Starting OneDrive and Photos cache cleanup...")
    worker.status_updated.emit("Cleaning: OneDrive / Photos Cache")
    
    base = Path(os.getenv("LOCALAPPDATA"))
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    # OneDrive cache
    onedrive_path = str(base / "Microsoft" / "OneDrive")
    success, failed, freed = delete_folder_contents(onedrive_path, log_file, worker)
    total_success += success
    total_failed += failed
    total_freed += freed
    
    # Check if worker should stop
    if not worker.is_running:
        return total_success, total_failed, total_freed
    
    # Photos app cache
    photos_folders = list((base / "Packages").glob("Microsoft.Windows.Photos_*"))
    
    for pf in photos_folders:
        if not worker.is_running:
            break
        
        photos_cache = str(pf / "LocalCache")
        success, failed, freed = delete_folder_contents(photos_cache, log_file, worker)
        total_success += success
        total_failed += failed
        total_freed += freed
    
    log_info(log_file, f"OneDrive and Photos cache cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_webcache(log_file, worker):
    r"""
    Clean Windows WebCache (File History, etc.).
    Location: %LOCALAPPDATA%\Microsoft\Windows\WebCache
    """
    path = str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "WebCache")
    return generic_folder_cleanup(
        "WebCache (File History)",
        path,
        log_file,
        worker
    )

def cleanup_icon_cache(log_file, worker):
    r"""
    Clean Windows icon cache file.
    Location: %LOCALAPPDATA%\IconCache.db
    """
    log_info(log_file, "Starting icon cache cleanup...")
    worker.status_updated.emit("Cleaning: Icon Cache")
    
    icon_cache_path = str(Path(os.getenv("LOCALAPPDATA")) / "IconCache.db")
    
    success = 0
    failed = 0
    freed = 0
    
    if os.path.exists(icon_cache_path):
        try:
            # Get file size before deletion
            file_size = os.path.getsize(icon_cache_path)
            
            # Delete the file
            os.remove(icon_cache_path)
            
            success = 1
            freed = file_size
            log_success(log_file, f"Deleted icon cache: {icon_cache_path}")
            
        except (PermissionError, OSError) as e:
            failed = 1
            log_failure(log_file, f"Delete icon cache: {icon_cache_path}", str(e))
    else:
        log_info(log_file, f"Icon cache file not found: {icon_cache_path}")
    
    log_info(log_file, f"Icon cache cleanup completed - Success: {success}, "
                      f"Failed: {failed}, Freed: {format_size(freed)}")
    
    return success, failed, freed

def cleanup_rdp_cache(log_file, worker):
    r"""
    Clean Remote Desktop Client cache.
    Location: %LOCALAPPDATA%\Microsoft\Terminal Server Client\Cache
    """
    path = str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Terminal Server Client" / "Cache")
    return generic_folder_cleanup(
        "RDP Cache",
        path,
        log_file,
        worker
    )

def cleanup_inetcache(log_file, worker):
    r"""
    Clean Internet Explorer and legacy Edge cache.
    Location: %LOCALAPPDATA%\Microsoft\Windows\INetCache
    """
    path = str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "INetCache")
    return generic_folder_cleanup(
        "INetCache (IE/Legacy Edge)",
        path,
        log_file,
        worker
    )

def cleanup_browser_caches(log_file, worker):
    r"""
    Clean caches for various web browsers.
    Browsers: Chrome, Edge, Opera, Brave, Firefox
    """
    log_info(log_file, "Starting browser cache cleanup...")
    worker.status_updated.emit("Cleaning: Browser Caches")
    
    LOCAL = Path(os.getenv("LOCALAPPDATA"))
    APPDATA = Path(os.getenv("APPDATA"))
    
    # Chromium-based browsers cache paths
    chromium_browsers = [
        "Google\\Chrome",
        "Microsoft\\Edge",
        "Opera Software\\Opera Stable",
        "BraveSoftware\\Brave-Browser"
    ]
    
    chromium_folders = []
    
    # Add Cache folders
    for browser in chromium_browsers:
        chromium_folders.append(LOCAL / browser / "User Data" / "Default" / "Cache")
    
    # Add GPUCache folders
    for browser in chromium_browsers:
        chromium_folders.append(LOCAL / browser / "User Data" / "Default" / "GPUCache")
    
    # Add Code Cache folders
    for browser in chromium_browsers:
        chromium_folders.append(LOCAL / browser / "User Data" / "Default" / "Code Cache")
    
    total_success = 0
    total_failed = 0
    total_freed = 0
    
    # Clean Chromium caches
    for cache_path in chromium_folders:
        if not worker.is_running:
            break
        
        success, failed, freed = delete_folder_contents(str(cache_path), log_file, worker)
        total_success += success
        total_failed += failed
        total_freed += freed
    
    # Firefox cache
    firefox_cache_pattern = str(APPDATA / "Mozilla" / "Firefox" / "Profiles" / "*" / "cache2")
    firefox_caches = glob.glob(firefox_cache_pattern)
    
    for profile in firefox_caches:
        if not worker.is_running:
            break
        
        success, failed, freed = delete_folder_contents(profile, log_file, worker)
        total_success += success
        total_failed += failed
        total_freed += freed
    
    log_info(log_file, f"Browser cache cleanup completed - Success: {total_success}, "
                      f"Failed: {total_failed}, Freed: {format_size(total_freed)}")
    
    return total_success, total_failed, total_freed

def cleanup_winsxs(log_file, worker):
    r"""
    Run DISM to clean WinSxS component store.
    This uses the Windows Deployment Image Servicing and Management tool.
    
    IMPORTANT: This function captures DISM output instead of showing a console window.
    """
    log_info(log_file, "Starting WinSxS cleanup using DISM...")
    worker.status_updated.emit("Cleaning: WinSxS (DISM) - This may take several minutes...")
    
    try:
        # Run DISM without creating a new console window
        # Capture output for logging
        result = subprocess.run(
            ["Dism.exe", "/Online", "/Cleanup-Image", "/StartComponentCleanup"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Log DISM output
        log_info(log_file, "DISM output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                log_info(log_file, f"  {line.strip()}")
        
        log_success(log_file, "WinSxS DISM cleanup completed successfully")
        
        # DISM doesn't report specific file counts, so return symbolic success
        return 1, 0, 0
        
    except subprocess.CalledProcessError as e:
        log_failure(log_file, "DISM cleanup operation", f"Process returned error code: {e.returncode}")
        
        # Log error output if available
        if e.stderr:
            log_info(log_file, "DISM error output:")
            for line in e.stderr.split('\n'):
                if line.strip():
                    log_info(log_file, f"  {line.strip()}")
        
        return 0, 1, 0
        
    except Exception as e:
        log_failure(log_file, "DISM cleanup operation", str(e))
        return 0, 1, 0

# =============================================================================
# TOOLTIP DESCRIPTIONS
# =============================================================================

TOOLTIPS = {
    "Windows Update Remnants": 
        "Cleans downloaded Windows Update files\n"
        "Location: C:\\Windows\\SoftwareDistribution\\Download\n"
        "Deletes: .cab, .msu, temporary update files\n"
        "Safe to clean - Windows will re-download if needed",
    
    "Delivery Optimization Cache": 
        "Cleans peer-to-peer update delivery cache\n"
        "Location: C:\\ProgramData\\Microsoft\\Windows\\DeliveryOptimization\n"
        "Deletes: Cached update files shared with other PCs\n"
        "Safe - doesn't affect already installed updates",
    
    "WinSxS Cleanup (DISM)": 
        "Runs DISM system cleanup tool\n"
        "Command: Dism.exe /Online /Cleanup-Image /StartComponentCleanup\n"
        "Cleans: Old component versions from WinSxS store\n"
        "Requires Admin rights - can free significant space\n"
        "Note: Progress shown in UI, may take 5-15 minutes",
    
    "Browser Caches": 
        "Cleans cache for multiple browsers\n"
        "Browsers: Chrome, Edge, Opera, Brave, Firefox\n"
        "Locations: AppData\\Local\\[Browser]\\User Data\\Default\\Cache\n"
        "Deletes: Temporary web files, images, scripts\n"
        "Safe - websites will reload slightly slower next visit",
    
    "Explorer Icon + Thumbnail Cache": 
        "Cleans Windows Explorer visual caches\n"
        "Location: %LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\n"
        "Deletes: iconcache.db, thumbcache files\n"
        "Safe - Explorer will rebuild cache automatically",
    
    "GPU Shader Cache": 
        "Cleans graphics card shader caches\n"
        "Locations: NVIDIA/DXCache, NVIDIA/GLCache, AMD/DxCache\n"
        "Deletes: Compiled shader files for games and applications\n"
        "Safe - shaders will recompile when needed (may cause brief stutter)",
    
    "Windows Store + UWP Cache": 
        "Cleans Microsoft Store and Universal App caches\n"
        "Location: %LOCALAPPDATA%\\Packages\\[App]_*\\LocalCache\n"
        "Deletes: UWP app temporary files, Store cache\n"
        "Safe - apps may take longer to load next time",
    
    "Crash Dumps": 
        "Cleans system and application crash files\n"
        "Locations: C:\\Windows\\Minidump, %LOCALAPPDATA%\\CrashDumps\n"
        "Deletes: .dmp, .hdmp crash dump files\n"
        "Safe - only removes diagnostic files after crashes",
    
    "WER Logs": 
        "Cleans Windows Error Reporting logs\n"
        "Location: C:\\ProgramData\\Microsoft\\Windows\\WER\n"
        "Deletes: Error report queues and archives\n"
        "Safe - removes old error reports sent to Microsoft",
    
    "DirectX Shader Cache": 
        "Cleans DirectX shader cache\n"
        "Location: %USERPROFILE%\\AppData\\Local\\D3DSCache\n"
        "Deletes: Compiled DirectX shader files\n"
        "Safe - games will recompile shaders on next launch",
    
    "Windows Logs": 
        "Cleans system log files\n"
        "Locations: C:\\Windows\\Logs, C:\\Windows\\System32\\LogFiles\n"
        "Deletes: .evtx, .log, .etl system log files\n"
        "Warning: Removes system event history - useful for troubleshooting",
    
    "OneDrive / Photos Cache": 
        "Cleans OneDrive and Photos app caches\n"
        "Locations: OneDrive settings cache, Photos app cache\n"
        "Deletes: Temporary sync files, photo thumbnails\n"
        "Safe - OneDrive will resync, Photos will rebuild cache",
    
    "Prefetch Files": 
        "Cleans Windows Prefetch files\n"
        "Location: C:\\Windows\\Prefetch\n"
        "Deletes: .pf files that speed up application loading\n"
        "Safe - Windows will recreate them, apps may load slower initially",
    
    "User Temp Files": 
        "Cleans user temporary files\n"
        "Location: %LOCALAPPDATA%\\Temp\n"
        "Deletes: Temporary files created by user applications\n"
        "Safe - applications will create new temp files as needed",
    
    "Windows Temp Files": 
        "Cleans system temporary files\n"
        "Location: C:\\Windows\\Temp\n"
        "Deletes: System-wide temporary files\n"
        "Safe - system and applications will create new temp files",
    
    "WebCache (File History)": 
        "Cleans Windows WebCache database\n"
        "Location: %LOCALAPPDATA%\\Microsoft\\Windows\\WebCache\n"
        "Deletes: File history, jump lists, and activity history cache\n"
        "Safe - removes cached file and browsing history",
    
    "Icon Cache": 
        "Cleans Windows icon cache\n"
        "Location: %LOCALAPPDATA%\\IconCache.db\n"
        "Deletes: System icon cache file\n"
        "Safe - Windows will rebuild it, custom folder icons may temporarily disappear",
    
    "RDP Cache": 
        "Cleans Remote Desktop Client cache\n"
        "Location: %LOCALAPPDATA%\\Microsoft\\Terminal Server Client\\Cache\n"
        "Deletes: Cached bitmaps from Remote Desktop sessions\n"
        "Safe - removes temporary RDP session data",
    
    "INetCache (IE/Legacy Edge)": 
        "Cleans Internet Explorer and legacy Edge cache\n"
        "Location: %LOCALAPPDATA%\\Microsoft\\Windows\\INetCache\n"
        "Deletes: Temporary internet files from IE/old Edge\n"
        "Safe - legacy browsers will rebuild cache"
}

# =============================================================================
# MAIN UI CLASS
# =============================================================================

class CleanerUI(QWidget):
    """
    Main application window for the Windows Cache Cleaner.
    Provides a user interface for selecting and running cleanup operations.
    """
    
    def __init__(self):
        """
        Initialize the main window and all UI components.
        """
        super().__init__()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} by Rane 🧹✨")
        self.setWindowIcon(QIcon('windows_cache_cleaner.ico'))
        
        # Get Windows accent colors for theming
        self.accent_color = get_windows_accent_color()
        self.accent_hover = get_darker_color(self.accent_color, HOVER_DARKNESS_FACTOR)
        self.accent_pressed = get_darker_color(self.accent_color, PRESSED_DARKNESS_FACTOR)
        
        # Initialize worker thread reference
        self.worker = None
        
        # Create main layout
        self.main_layout = QVBoxLayout()
        
        # Define cleanup operations mapping
        # This dictionary maps checkbox labels to their cleanup functions
        self.checks = {
            "Windows Temp Files": cleanup_windows_temp,
            "User Temp Files": cleanup_user_temp,
            "Prefetch Files": cleanup_prefetch,
            "Explorer Icon + Thumbnail Cache": cleanup_explorer_cache,
            "Icon Cache": cleanup_icon_cache,
            "Windows Update Remnants": cleanup_windows_update,
            "Delivery Optimization Cache": cleanup_delivery_opt,
            "Crash Dumps": cleanup_crash_dumps,
            "WER Logs": cleanup_wer_logs,
            "Windows Logs": cleanup_windows_logs,
            "DirectX Shader Cache": cleanup_d3d_cache,
            "GPU Shader Cache": cleanup_gpu_cache,
            "RDP Cache": cleanup_rdp_cache,
            "INetCache (IE/Legacy Edge)": cleanup_inetcache,
            "OneDrive / Photos Cache": cleanup_onedrive_photos,
            "Windows Store + UWP Cache": cleanup_store_cache,
            "Browser Caches": cleanup_browser_caches,
            "WebCache (File History)": cleanup_webcache,
            "WinSxS Cleanup (DISM)": cleanup_winsxs,
        }
        
        # Load saved configuration
        self.config = load_config()
        
        # Initialize checkbox storage
        self.checkbox_widgets = {}
        
        # Create UI components
        self.init_ui()
        
        # Apply dynamic styling
        self.apply_dynamic_styles()
        
        # Set window size and position
        self.adjustSize()
        self.center_on_screen()
        self.setFixedSize(self.size())
    
    def init_ui(self):
        """
        Initialize all UI components.
        Creates the checkbox grid, buttons, progress indicators, and status display.
        """
        # Create checkbox grid layout
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)  # Space between columns
        grid_layout.setVerticalSpacing(5)  # Space between rows
        
        # Populate grid with checkboxes (6 per column)
        row = 0
        col = 0
        for label in self.checks:
            # Create checkbox
            cb = QCheckBox(label)
            
            # Set state from saved config (default to False if not found)
            cb.setChecked(self.config.get(label, False))
            
            # Add tooltip with detailed information
            if label in TOOLTIPS:
                cb.setToolTip(TOOLTIPS[label])
            
            # Store checkbox reference
            self.checkbox_widgets[label] = cb
            
            # Add to grid
            grid_layout.addWidget(cb, row, col)
            
            # Move to next row
            row += 1
            
            # Start new column after MAX_ROWS_PER_COLUMN rows
            if row >= MAX_ROWS_PER_COLUMN:
                row = 0
                col += 1
        
        # Add grid to main layout
        self.main_layout.addLayout(grid_layout)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create Select All button
        self.select_all_btn = QPushButton("Select All 📋")
        self.select_all_btn.setToolTip("Select all cleanup options")
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        button_layout.addWidget(self.select_all_btn)
        
        # Create Analyze button (calculates sizes without cleaning)
        self.analyze_btn = QPushButton("Analyze 🔍")
        self.analyze_btn.setToolTip("Calculate how much space will be freed (without cleaning)")
        self.analyze_btn.clicked.connect(self.analyze_cleanup)
        button_layout.addWidget(self.analyze_btn)
        
        # Create Run Cleanup button
        self.run_btn = QPushButton("Run Cleanup 🚀")
        self.run_btn.setToolTip("Execute the selected cleanup operations")
        self.run_btn.clicked.connect(self.run_cleanup)
        button_layout.addWidget(self.run_btn)
        
        # Create Stop button (initially disabled)
        self.stop_btn = QPushButton("Stop ⛔")
        self.stop_btn.setToolTip("Cancel the current cleanup operation")
        self.stop_btn.clicked.connect(self.stop_cleanup)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        # Add button layout to main layout
        self.main_layout.addLayout(button_layout)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.main_layout.addWidget(self.progress_bar)
        
        # Create status label
        self.status_label = QLabel("Status: Ready 💤")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)
        
        # Create operation log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        self.log_display.setPlaceholderText("Operation log will appear here...")
        self.main_layout.addWidget(self.log_display)
        
        # Create info label
        info_label = QLabel("ℹ️ Hover over any option to see detailed information • "
                          "Made with ❤️ by Rane")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888; font-size: 10px; margin: 10px;")
        self.main_layout.addWidget(info_label)
        
        # Set the main layout
        self.setLayout(self.main_layout)
    
    def center_on_screen(self):
        """
        Center the window on the screen.
        """
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        window_rect = self.frameGeometry()
        center_point = screen_rect.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
    
    def apply_dynamic_styles(self):
        """
        Apply dynamic styles to the UI using the detected Windows accent color.
        """
        dynamic_style = f"""
            QCheckBox {{
                spacing: 8px;
                padding: 5px;
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid #7a7a7a;
                border-radius: 2px;
                background-color: #ffffff;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.accent_color};
                border: 1px solid {self.accent_color};
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {self.accent_hover};
                border: 1px solid {self.accent_hover};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {self.accent_color};
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
            QPushButton:disabled {{
                background-color: #666;
            }}
            QProgressBar {{
                border: 1px solid #7a7a7a;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }}
            QProgressBar::chunk {{
                background-color: {self.accent_color};
                border-radius: 3px;
            }}
            QTextEdit {{
                background-color: #2d2d2d;
                color: #f0f0f0;
                border: 1px solid #7a7a7a;
                border-radius: 4px;
                padding: 5px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 10px;
            }}
            QToolTip {{
                background-color: #ffffe0;
                color: #000000;
                border: 1px solid #000000;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
            }}
        """
        self.setStyleSheet(dynamic_style)
    
    def toggle_select_all(self):
        """
        Toggle all checkboxes on or off.
        """
        # Check if any checkbox is unchecked
        any_unchecked = any(not cb.isChecked() for cb in self.checkbox_widgets.values())
        
        # Set all checkboxes to the same state
        new_state = any_unchecked
        for cb in self.checkbox_widgets.values():
            cb.setChecked(new_state)
        
        # Update button text
        self.select_all_btn.setText("Deselect All 📋" if new_state else "Select All 📋")
    
    def analyze_cleanup(self):
        """
        Analyze selected cleanup operations without actually cleaning.
        Calculates and displays how much space will be freed.
        """
        # Get selected operations
        selected = [label for label, cb in self.checkbox_widgets.items() if cb.isChecked()]
        
        if not selected:
            QMessageBox.warning(self, "No Selection", 
                              "Please select at least one cleanup option to analyze. 🤔")
            return
        
        # Disable buttons during analysis
        self.update_button_states(analyzing=True)
        self.status_label.setText("Analyzing selected locations... 🔍")
        self.progress_bar.setValue(0)
        self.log_display.clear()
        
        # Process events to update UI
        QApplication.processEvents()
        
        # Analyze each selected location
        total_size = 0
        total_files = 0
        analysis_text = "📊 Analysis Results:\n\n"
        
        total_operations = len(selected)
        for idx, operation_name in enumerate(selected):
            # Update progress
            progress = int((idx / total_operations) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Analyzing: {operation_name}...")
            QApplication.processEvents()
            
            # Get the path(s) for this operation
            # This is a simplified version - in a full implementation,
            # each cleanup function would have a corresponding "get_paths" function
            size, count = self.get_operation_size(operation_name)
            
            if size > 0:
                total_size += size
                total_files += count
                analysis_text += f"✓ {operation_name}: {format_size(size)} ({count:,} files)\n"
            else:
                analysis_text += f"○ {operation_name}: Empty or not found\n"
        
        # Set progress to 100%
        self.progress_bar.setValue(100)
        
        # Display results
        analysis_text += f"\n{'='*50}\n"
        analysis_text += f"📦 Total space that will be freed: {format_size(total_size)}\n"
        analysis_text += f"📄 Total files to be deleted: {total_files:,}\n"
        analysis_text += f"{'='*50}\n"
        
        self.log_display.setPlainText(analysis_text)
        self.status_label.setText(f"Analysis complete: {format_size(total_size)} can be freed ✅")
        
        # Re-enable buttons
        self.update_button_states(analyzing=False)
    
    def get_operation_size(self, operation_name):
        """
        Get the size and file count for a specific cleanup operation.
        
        Args:
            operation_name (str): Name of the operation
            
        Returns:
            tuple: (total_size_bytes, file_count)
        """
        # Map operation names to their paths
        path_map = {
            "Windows Temp Files": [r"C:\Windows\Temp"],
            "User Temp Files": [str(Path(os.getenv("LOCALAPPDATA")) / "Temp")],
            "Prefetch Files": [r"C:\Windows\Prefetch"],
            "Windows Update Remnants": [r"C:\Windows\SoftwareDistribution\Download"],
            "Delivery Optimization Cache": [r"C:\ProgramData\Microsoft\Windows\DeliveryOptimization"],
            "Explorer Icon + Thumbnail Cache": [str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "Explorer")],
            "Icon Cache": [str(Path(os.getenv("LOCALAPPDATA")) / "IconCache.db")],
            "WER Logs": [r"C:\ProgramData\Microsoft\Windows\WER"],
            "DirectX Shader Cache": [str(Path.home() / "AppData" / "Local" / "D3DSCache")],
            "RDP Cache": [str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Terminal Server Client" / "Cache")],
            "INetCache (IE/Legacy Edge)": [str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "INetCache")],
            "WebCache (File History)": [str(Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Windows" / "WebCache")],
        }
        
        # Get paths for this operation
        paths = path_map.get(operation_name, [])
        
        total_size = 0
        total_files = 0
        
        for path in paths:
            size, count = get_folder_size(path)
            total_size += size
            total_files += count
        
        return total_size, total_files
    
    def run_cleanup(self):
        """
        Start the cleanup process for selected operations.
        """
        # Get selected operations
        selected_ops = {}
        for label, cb in self.checkbox_widgets.items():
            if cb.isChecked():
                selected_ops[label] = self.checks[label]
        
        if not selected_ops:
            QMessageBox.warning(self, "No Selection", 
                              "Please select at least one cleanup option. 🤔")
            return
        
        # Show confirmation dialog
        op_list = "\n• ".join(selected_ops.keys())
        confirm = QMessageBox.question(
            self, 
            "Confirm Cleanup",
            f"You are about to clean:\n\n• {op_list}\n\n"
            f"This action cannot be undone. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Save current configuration
        for label, cb in self.checkbox_widgets.items():
            self.config[label] = cb.isChecked()
        save_config(self.config)
        
        # Setup logging
        ensure_log_dir()
        log_filename = generate_log_filename()
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.log_display.clear()
        self.log_display.append("🚀 Starting cleanup operations...\n")
        
        # Update button states
        self.update_button_states(cleaning=True)
        
        # Create and start worker thread
        self.worker = CleanupWorker(selected_ops, log_filename)
        
        # Connect signals
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.status_updated.connect(self.on_status_updated)
        self.worker.operation_started.connect(self.on_operation_started)
        self.worker.operation_completed.connect(self.on_operation_completed)
        self.worker.task_completed.connect(self.on_task_completed)
        self.worker.error_occurred.connect(self.on_error_occurred)
        
        # Start the worker
        self.worker.start()
    
    def stop_cleanup(self):
        """
        Stop the currently running cleanup operation.
        """
        if self.worker and self.worker.isRunning():
            # Ask for confirmation
            confirm = QMessageBox.question(
                self,
                "Stop Cleanup",
                "Are you sure you want to stop the cleanup?\n\n"
                "Already deleted files cannot be recovered.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.log_display.append("\n⛔ Stopping cleanup (please wait)...\n")
                self.status_label.setText("Cancelling cleanup... ⏳")
    
    def on_progress_updated(self, value):
        """
        Handle progress updates from the worker thread.
        
        Args:
            value (int): Progress percentage (0-100)
        """
        self.progress_bar.setValue(value)
    
    def on_status_updated(self, message):
        """
        Handle status updates from the worker thread.
        
        Args:
            message (str): Status message
        """
        self.status_label.setText(message)
    
    def on_operation_started(self, operation_name):
        """
        Handle operation start notifications from the worker thread.
        
        Args:
            operation_name (str): Name of the operation that started
        """
        self.log_display.append(f"📂 Starting: {operation_name}")
    
    def on_operation_completed(self, operation_name, success, failed, bytes_freed):
        """
        Handle operation completion notifications from the worker thread.
        
        Args:
            operation_name (str): Name of the operation
            success (int): Number of successful operations
            failed (int): Number of failed operations
            bytes_freed (int): Bytes freed
        """
        self.log_display.append(
            f"✅ Completed: {operation_name} - "
            f"Success: {success}, Failed: {failed}, "
            f"Freed: {format_size(bytes_freed)}\n"
        )
    
    def on_error_occurred(self, error_message):
        """
        Handle error notifications from the worker thread.
        
        Args:
            error_message (str): Error message
        """
        self.log_display.append(f"❌ Error: {error_message}\n")
    
    def on_task_completed(self, ops_count, success, failed, size_freed):
        """
        Handle task completion notification from the worker thread.
        
        Args:
            ops_count (int): Number of operations performed
            success (int): Total successful operations
            failed (int): Total failed operations
            size_freed (int): Total bytes freed
        """
        # Update UI
        self.progress_bar.setValue(100)
        self.status_label.setText("Cleanup complete! ✨")
        
        # Update log display
        self.log_display.append("\n" + "="*50)
        self.log_display.append("🎉 CLEANUP COMPLETE!")
        self.log_display.append("="*50)
        self.log_display.append(f"Operations performed: {ops_count}")
        self.log_display.append(f"Successful operations: {success}")
        self.log_display.append(f"Failed operations: {failed}")
        self.log_display.append(f"Space freed: {format_size(size_freed)}")
        self.log_display.append("="*50 + "\n")
        
        # Show completion message
        message = (
            f"Cleanup completed successfully! 🎉\n\n"
            f"Operations performed: {ops_count}\n"
            f"Successful file operations: {success}\n"
            f"Failed file operations: {failed}\n"
            f"Space freed: {format_size(size_freed)}\n\n"
            f"Log file saved to:\n{self.worker.log_file_path}"
        )
        
        QMessageBox.information(self, "Cleanup Complete", message)
        
        # Re-enable buttons
        self.update_button_states(cleaning=False)
        
        # Clean up worker
        self.worker = None
    
    def update_button_states(self, cleaning=False, analyzing=False):
        """
        Update the enabled/disabled state of buttons based on current activity.
        
        Args:
            cleaning (bool): Whether cleanup is in progress
            analyzing (bool): Whether analysis is in progress
        """
        # Determine if any operation is in progress
        busy = cleaning or analyzing
        
        # Update button states
        self.select_all_btn.setEnabled(not busy)
        self.analyze_btn.setEnabled(not busy)
        self.run_btn.setEnabled(not busy)
        self.stop_btn.setEnabled(cleaning)  # Only enable stop during cleanup
        
        # Disable checkboxes during operations
        for cb in self.checkbox_widgets.values():
            cb.setEnabled(not busy)
    
    def closeEvent(self, event):
        """
        Handle window close event.
        Ensures worker thread is stopped before closing.
        
        Args:
            event: Close event
        """
        # Check if worker is running
        if self.worker and self.worker.isRunning():
            # Ask for confirmation
            confirm = QMessageBox.question(
                self,
                "Cleanup In Progress",
                "Cleanup is still running. Are you sure you want to exit?\n\n"
                "Already deleted files cannot be recovered.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Stop worker
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Check for admin rights
    if not is_admin():
        # Request UAC elevation
        try:
            script_path = os.path.abspath(__file__)
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{script_path}"',
                None,
                1
            )
            
            if result <= 32:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Failed to request administrator privileges.\n\n"
                    "Please run as Administrator manually.",
                    "Elevation Failed",
                    0x10
                )
            sys.exit()
            
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Error requesting admin rights: {str(e)}\n\n"
                "Please run as Administrator manually.",
                "Error",
                0x10
            )
            sys.exit()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Set application font to Comic Sans MS (matching your style)
    comic_sans_font = QFont("Comic Sans MS", 9)
    app.setFont(comic_sans_font)
    
    # Try to load application icon
    try:
        icon_path = "windows_cache_cleaner.ico"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass  # Icon loading is optional
    
    # Get accent colors for global styling
    accent_color = get_windows_accent_color()
    accent_hover = get_darker_color(accent_color, HOVER_DARKNESS_FACTOR)
    accent_pressed = get_darker_color(accent_color, PRESSED_DARKNESS_FACTOR)
    
    # Apply global application styles
    app.setStyleSheet(f"""
        QWidget {{
            background-color: #2d2d2d;
            color: #f0f0f0;
            font-family: "Comic Sans MS", "Segoe UI", Arial, sans-serif;
        }}
        QLabel {{
            color: #f0f0f0;
        }}
    """)
    
    # Create and show main window
    window = CleanerUI()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())
