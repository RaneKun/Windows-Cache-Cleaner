# 🏗️ Building Windows Cache Cleaner to EXE

This guide walks you through turning the Python script into a standalone `.exe` file that anyone can run — no Python installation needed on their end.

---

## 📋 What You Need First

Just two things:

1. **Python installed on your PC** (you already have this if you ran the main script before)
2. **These three files in the same folder:**
   - `windows_cache_cleaner.py` — the app itself
   - `windows_cache_cleaner.ico` — the icon (optional, but nice to have)
   - `build_exe.bat` — the build script that does the work

That's it. You don't need to install anything else — the build script handles the rest.

---

## 🚀 How to Build It

1. **Open the folder** with all three files in it
2. **Double-click** `build_exe.bat`
3. **Wait 2-5 minutes** while it does its thing
4. **Done!** Your `.exe` is sitting right there in the same folder

That's genuinely all there is to it.

---

## 🤔 What the Build Script Does For You

You don't need to know any of this to use it, but here's what's happening behind the scenes so nothing feels mysterious:

- ✅ Makes sure Python is installed and is a recent enough version
- ✅ Installs PyInstaller if you don't already have it
- ✅ Checks that your app file is where it's supposed to be
- ✅ Builds the `.exe`
- ✅ Moves the finished `.exe` right next to the build script
- ✅ Cleans up all the temporary build files so your folder stays tidy

When it's done, your folder looks basically the same as before — plus one shiny new `Windows Cache Cleaner.exe`.

---

## 📂 What Your Folder Looks Like After Building

**Before:**
```
Your Folder/
├── windows_cache_cleaner.py
├── windows_cache_cleaner.ico
└── build_exe.bat
```

**After:**
```
Your Folder/
├── windows_cache_cleaner.py
├── windows_cache_cleaner.ico
├── build_exe.bat
└── Windows Cache Cleaner.exe     ⭐ Your new .exe!
```

No leftover `build` folder, no `dist` folder, no `.spec` file — the script cleans all of that up automatically.

---

## ✅ Testing It

1. Find `Windows Cache Cleaner.exe` in your folder
2. **Right-click it → Run as administrator**
3. Make sure the window opens, the icon looks right, and everything works

If it opens fine, you're done. 🎉

---

## 📦 Sharing It With Others

Once you've got your `.exe`, you can:

- **Copy it anywhere** — desktop, USB stick, another PC
- **Send it to anyone** — they don't need Python installed
- **Make a shortcut** — right-click → Send to → Desktop

**Heads up on file size:** it'll be around 30–35 MB, since the `.exe` carries its own little Python setup inside. That's normal.

---

## 🛠️ If Something Goes Wrong

Here are the most common hiccups and how to fix them:

**"Python is not installed or not on PATH"**
You either don't have Python installed, or it wasn't added to your PATH when you installed it. Reinstall Python from [python.org](https://www.python.org/) and make sure to tick **"Add Python to PATH"** during setup.

**"Python 3.10+ is required"**
Your Python is too old. Grab the latest version from [python.org](https://www.python.org/) and try again.

**"pip is not available"**
Python was installed without pip, which is unusual but fixable. Open a command prompt and run:
```
python -m ensurepip --upgrade
```

**"Cannot reach pypi.org"**
The build script needs internet access to download PyInstaller if you don't already have it. Connect to the internet and try again.

**Icon doesn't show up on the .exe**
Make sure `windows_cache_cleaner.ico` is actually in the folder with the other files. If it's missing, the build still works — you just won't get a custom icon.

**"Failed to move the executable"**
An old copy of `Windows Cache Cleaner.exe` is probably still open somewhere. Close it, then run the build script again.

**Build failed with errors**
Try this in order:
1. Make sure all three files are in the same folder
2. Delete the `build` and `dist` folders if they exist, then rebuild
3. Make sure no other programs are using those files

---

## 🔒 A Note About Antivirus

Some antivirus programs flag `.exe` files built this way as suspicious. **This is a false alarm** — it happens because of how the Python packaging tool works, not because there's anything wrong with your app.

If your antivirus complains:

- **Whitelist the `.exe`** — tell your antivirus to leave it alone
- **Report it as a false positive** — most vendors have a form for this
- **Build it yourself** — which you're already doing, so you know exactly what's in it

---

## 💡 A Few Tips

- **Keep the icon file** — it gets baked into the `.exe`, so the `.exe` works fine on its own afterward
- **Test before sharing** — always run the `.exe` once yourself first
- **Don't delete the source `.py` file** — you'll need it if you ever want to rebuild
- **Close the old `.exe`** before rebuilding — otherwise the new one can't take its place

---

## 🎯 The Short Version

**Double-click `build_exe.bat`. Wait. Done.**

Your `.exe` appears in the same folder. No cleanup needed — it's all handled automatically. 🎉

---

**Happy building! 🔨**
