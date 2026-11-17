#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

CWD = Path.cwd()
SOURCE = Path(r"C:\Users\Shrikant\.gemini\antigravity\scratch\gram-panchayat-portal")

print("\n" + "=" * 65)
print("  🚀 GRAM PANCHAYAT PORTAL - ONE-CLICK MASTER BUILD AGENT")
print("  ಗ್ರಾಮ ಪಂಚಾಯತ್ ಡಿಜಿಟಲ್ ಕುಂದುಕೊರತೆ ನಿವಾರಣಾ ಪೋರ್ಟಲ್")
print("=" * 65 + "\n")

# 1. Copy all project files directly into the current VS Code workspace
if SOURCE.exists() and SOURCE != CWD:
    print("[1/3] Importing all backend & frontend files into your VS Code folder...")
    for item in SOURCE.iterdir():
        if item.name not in ["venv", ".git"]:
            dest = CWD / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    print("  ✔ Successfully generated all code files in your folder!")

# 2. Check and install packages
print("\n[2/3] Verifying Python packages (Flask, Werkzeug, Pillow)...")
try:
    import flask
    import werkzeug
    from PIL import Image
    print("  ✔ Packages ready!")
except ImportError:
    print("  ⌛ Installing via pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask>=2.3.0", "werkzeug>=2.3.0", "pillow>=10.0.0"])
    print("  ✔ Packages installed successfully!")

# 3. Launch the Application
print("\n[3/3] Starting Website at http://127.0.0.1:5000...")
os.chdir(str(CWD))
sys.path.insert(0, str(CWD))

import app
app.init_database()

port = 5000
print("\n" + "=" * 65)
print(f"  🌐 HOMEPAGE:        http://127.0.0.1:{port}")
print(f"  🧑‍🌾 CITIZEN LOGIN:   http://127.0.0.1:{port}/citizen/login")
print(f"  🏛️ OFFICIAL LOGIN:  http://127.0.0.1:{port}/admin/login")
print("=" * 65 + "\n")

import webbrowser
def open_browser():
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

import threading
threading.Thread(target=open_browser, daemon=True).start()

app.app.run(host="0.0.0.0", port=port, debug=False)
