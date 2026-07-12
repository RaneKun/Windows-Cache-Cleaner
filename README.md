# 🧹 Windows Cache Cleaner

<p align="center">
  <img src="windows_cache_cleaner.ico" alt="Windows Cache Cleaner Icon" width="128" height="128">
</p>

<p align="center">
  <strong>A simple, safe, and powerful tool to clean unnecessary cache files on Windows — without touching anything important.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Language-Python%203.12-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/GUI-PyQt6-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/License-RaneKun%20Open--Use-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Safe-No%20Critical%20Files%20Touched-brightgreen?style=for-the-badge">
</p>

---

## 📖 Overview

Windows Cache Cleaner is a user-friendly desktop application that helps you reclaim disk space by safely removing temporary files, cache data, and other unnecessary junk that accumulates over time on Windows systems.

**Version 2.0** brings a completely redesigned experience with multi-threading, real-time progress tracking, and an intuitive interface that makes cache cleaning effortless.

---

## ✨ Key Features

### 🎯 Smart & Safe Cleanup
- **20 Different Cleanup Options** — From browser caches to Windows Update remnants to dev tool caches
- **Safe by Design** — Only targets non-critical cache folders
- **Detailed Tooltips** — Hover over any option to see exactly what it cleans
- **Confirmation Dialogs** — Prevents accidental deletions

### ⚡ Powerful Performance
- **Non-Blocking UI** — Application stays responsive during cleanup
- **Real-Time Progress** — Live progress bar and status updates
- **Analyze Mode** — Preview how much space you'll free before cleaning
- **Cancellable Operations** — Stop cleanup at any time

### 📊 Transparency & Control
- **Live Operation Log** — See exactly what's being cleaned in real-time
- **Detailed Reports** — Shows files deleted, space freed, and any errors
- **Persistent Settings** — Remembers your cleanup preferences
- **Comprehensive Logs** — All operations logged to file for review

### 🎨 User Experience
- **Comic Sans MS UI** — Friendly, approachable interface
- **Windows Theme Integration** — Matches your system accent color
- **Select All / Analyze / Clean** — Three-step workflow
- **No Installation Required** — Portable standalone executable

---

## 🚀 What This Tool Cleans

This cleaner targets **only safe-to-remove cache folders**, including:

| Category | What Gets Cleaned | Typical Space Saved |
|----------|------------------|-------------------|
| 🗂️ **Temp Files** | Windows & User temporary files | 1-10 GB |
| 🐍 **Coding/Dev Tool Caches** | pip, conda, npm, Yarn caches | 500 MB - 10 GB |
| 🌐 **Browser Caches** | Chrome, Edge, Firefox, Opera, Brave | 500 MB - 5 GB |
| 📦 **Windows Update** | Downloaded update files | 500 MB - 5 GB |
| 🎮 **GPU Shader Cache** | NVIDIA, AMD shader compilations | 100 MB - 2 GB |
| 🏪 **Windows Store** | UWP app caches | 200 MB - 3 GB |
| 📸 **Thumbnails** | Icon and thumbnail caches | 50 MB - 500 MB |
| 💥 **Crash Dumps** | System and app crash files | 100 MB - 5 GB |
| 📝 **System Logs** | Windows event and error logs | 100 MB - 2 GB |
| ⚙️ **WinSxS** | Component store cleanup (via DISM) | 2 GB - 20 GB |
| ...and more! | Prefetch, WebCache, RDP cache, etc. | Variable |

**Total Potential Savings:** 5 GB to 50+ GB depending on system age and usage

---

## 📂 What's Included

```
Windows-Cache-Cleaner/
│
├── 📄 README.md                          ← You are here
├── 📄 LICENSE                            ← RaneKun Open-Use License
├── 📄 CHANGELOG.md                       ← Version history
│
├── 🖼️ windows_cache_cleaner.ico         ← Application icon
│
├── 🔧 windows_cache_cleaner_IMPROVED.py  ← Full source code (Python + PyQt6)
│
├── 🛠️ build_exe.bat                      ← Build script (Windows)
├── 🛠️ build_exe.py                       ← Build script (Python)
├── 📄 BUILD_INSTRUCTIONS.md              ← How to build the .exe
│
└── 📦 dist/
    └── Windows Cache Cleaner.exe         ← Standalone executable
```

---

## 🎮 How to Use

### Option 1: Standalone EXE (Recommended)

1. **Download** the latest release from the [Releases](https://github.com/RaneKun/Windows-Cache-Cleaner/releases) page
2. **Extract** the ZIP file
3. **Right-click** `Windows Cache Cleaner.exe` → **Run as administrator**
4. **Select** cleanup options (or click "Select All")
5. **Optional:** Click "Analyze 🔍" to preview space savings
6. **Click** "Run Cleanup 🚀"
7. **Wait** for completion and review the results

### Option 2: Run from Source

**Requirements:**
- Python 3.10 or higher
- PyQt6

**Steps:**
```bash
# Install dependencies
pip install PyQt6

# Run the application
python windows_cache_cleaner_IMPROVED.py
```

---

## 🛡️ Safety & Security

### What Makes This Tool Safe?

✅ **No Critical System Files** — Only cleans cache folders that Windows recreates automatically  
✅ **Admin Rights Required** — Ensures you're aware of what the tool is doing  
✅ **Detailed Tooltips** — Full transparency about what each option does  
✅ **Confirmation Dialogs** — Asks before making any changes  
✅ **Comprehensive Logging** — Everything is logged for review  
✅ **Open Source** — You can inspect the code yourself  

### Antivirus False Positives

**Note:** Some antivirus software may flag the `.exe` as suspicious. This is a **false positive** common with PyInstaller-built executables.

**Why this happens:**
- PyInstaller bundles the Python interpreter into the .exe
- This packaging method can resemble some malware packers
- The tool requires admin rights (which is flagged by heuristics)

**What you can do:**
- Check the source code yourself (it's fully available)
- Build the .exe yourself using the included build scripts
- Add the .exe to your antivirus whitelist
- Submit it to your antivirus vendor as a false positive

---

## 🎨 Screenshots

### Main Interface
*Clean, modern UI with checkbox options and real-time feedback*

### Analyze Mode
*Preview exactly how much space you'll free before cleaning*

### Live Operation Log
*Watch the cleanup happen in real-time with detailed status updates*

---

## 🔧 Building from Source

Want to build the `.exe` yourself?

### Quick Build (Windows):
1. Put all files in a folder
2. Double-click `build_exe.bat`
3. Wait 2-5 minutes
4. Find your `.exe` in the `dist` folder

### Manual Build:
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name "Windows Cache Cleaner" --icon=windows_cache_cleaner.ico --add-data "windows_cache_cleaner.ico;." windows_cache_cleaner_IMPROVED.py
```

See `BUILD_INSTRUCTIONS.md` for detailed build instructions.

---

## 📊 Version History

### v2.1.0 (Current)
**Coding/Dev Tool Cache Cleanup** — Adds a new option to clear out pip, conda, npm, and Yarn caches

**New Features:**
- New "Coding/Dev Tool Caches" cleanup option, placed right under "User Temp Files"
- Cleans pip cache, conda pkgs cache (anaconda3/miniconda3/.conda), npm cache, and Yarn cache
- Fully integrated with Analyze mode, tooltips, and checkbox persistence

**Changes:**
- Total cleanup options: 19 → 20

### v2.0.0
**Major Rewrite** — Complete overhaul with modern features

**New Features:**
- Multi-threaded cleanup (UI never freezes)
- Real-time progress bar and status updates
- Analyze mode (preview space savings)
- Live operation log
- Stop/cancel functionality
- Size tracking (shows exactly how much space freed)
- Confirmation dialogs
- Better error handling

**Improvements:**
- Comic Sans MS font throughout
- Windows accent color integration
- Proper app data directory (`%LOCALAPPDATA%\WindowsCacheCleaner`)
- Better code organization and documentation
- No debug print spam

**Bug Fixes:**
- Fixed UI freezing during cleanup
- Fixed missing Select All button functionality
- Fixed DISM cleanup console window issue

### v1.1.0
Initial public release

---

## 💡 Tips & Best Practices

1. **Run Regularly** — Weekly or monthly cleanups keep your system fresh
2. **Analyze First** — Use Analyze mode to see what you'll gain
3. **Close Browsers** — Close all browsers before cleaning browser caches
4. **Keep Logs** — Review logs if something seems off
5. **Safe Options** — Start with safe options, add more aggressive ones later

---

## 🐛 Known Issues

- **Antivirus False Positives** — See "Safety & Security" section above
- **Some Files May Be Locked** — Files in use won't be deleted (this is normal and safe)
- **DISM Takes Time** — WinSxS cleanup can take 5-15 minutes (be patient)

---

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome!

**Ways to contribute:**
- Report bugs via [Issues](https://github.com/RaneKun/Windows-Cache-Cleaner/issues)
- Suggest new cleanup locations (if safe)
- Share your experience and results
- Improve documentation
- Submit bug fixes (pull requests welcome)

---

## 📜 License

This project is released under the **RaneKun Open-Use License**.

### You CAN:
✅ Use the tool freely for personal use  
✅ Read and study the source code  
✅ Modify the code for personal use  
✅ Share the original or modified versions  
✅ Use it for educational purposes  

### You CANNOT:
❌ Sell this software or derivatives  
❌ Use it in commercial projects without permission  
❌ Remove or modify attribution to RaneKun  
❌ Claim it as your own work  

### You MUST:
✔️ Give proper credit to the original creator (RaneKun)  
✔️ Include the original license in any distributions  
✔️ Keep modifications open source (if distributed)  

**TL;DR:** Free for personal use. No selling. Keep it credited. 🙂

Full license text is available in the `LICENSE` file.

---

## 👤 Author

**Created by RaneKun**

- Icon designed by RaneKun
- UI/UX designed by RaneKun
- Code written by RaneKun

This is a hobby project built to help Windows users keep their systems clean and fast.

---

## 🙏 Credits & Acknowledgments

**Built with:**
- [Python](https://www.python.org/) — Programming language
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — GUI framework
- [PyInstaller](https://pyinstaller.org/) — Executable packager

**Inspired by:**
- CCleaner (before it got bloated)
- BleachBit
- The need for a simple, trustworthy cache cleaner

---

## 💬 Support & Feedback

- **Questions?** Open an [Issue](https://github.com/RaneKun/Windows-Cache-Cleaner/issues)
- **Found a bug?** Report it on [Issues](https://github.com/RaneKun/Windows-Cache-Cleaner/issues)
- **Feature request?** Let me know in [Discussions](https://github.com/RaneKun/Windows-Cache-Cleaner/discussions)

---

## ⚠️ Disclaimer

This tool is provided "as is" without warranty of any kind. While it only targets safe cache folders, use at your own risk. Always keep backups of important data.

The author is not responsible for any data loss or system issues that may occur from using this tool.

---

## 🌟 Star This Project!

If you find this tool useful, consider giving it a ⭐ on GitHub!

It helps others discover the project and motivates continued development.

---

<p align="center">
  <strong>Made with ❤️ by RaneKun</strong>
</p>

<p align="center">
  <sub>Keep your Windows clean, fast, and clutter-free! 🧹✨</sub>
</p>
