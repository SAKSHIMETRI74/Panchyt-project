#!/usr/bin/env python3
"""
Gram Panchayat Portal - Autonomous Builder & Management Agent
This script automates environment setup, dependency verification,
database migrations, health checks, and server execution directly in VS Code.
"""

import os
import sys
import subprocess
import sqlite3
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def print_banner():
    banner = r"""
  ========================================================================
   GRAM PANCHAYAT DIGITAL PORTAL - AUTONOMOUS BUILDER AGENT
   ಗ್ರಾಮ ಪಂಚಾಯತ್ ಡಿಜಿಟಲ್ ಕುಂದುಕೊರತೆ ನಿವಾರಣಾ ಪೋರ್ಟಲ್
  ========================================================================
    """
    print(banner)

def step(msg):
    print(f"\n[AGENT] -> {msg}")

def success(msg):
    print(f"[OK] {msg}")

def check_and_install_dependencies():
    step("Checking Python dependencies...")
    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        print("[!] requirements.txt not found. Skipping dependency check.")
        return

    try:
        import flask
        import werkzeug
        success("Core packages (Flask, Werkzeug) are already installed.")
    except ImportError:
        print("[*] Missing dependencies. Installing via pip...")
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
        subprocess.check_call(cmd)
        success("Dependencies installed successfully.")

def ensure_folders():
    step("Verifying private storage and directory structure...")
    private_uploads = BASE_DIR / "private_uploads"
    private_uploads.mkdir(parents=True, exist_ok=True)
    success(f"Protected evidence storage ready at: {private_uploads.name}/")

def initialize_database():
    step("Initializing SQLite Database & Seeding Accounts...")
    try:
        from database import init_db
        init_db()
        success("Database tables created and default accounts verified:")
        print("     • Admin (PDO): Phone=9876543210 | Pass=PanchayatAdmin@2026")
        print("     • Citizen Test: Phone=9845012345 | Pass=Citizen@123")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")

def run_tests():
    step("Running automated unit test suite...")
    test_dir = BASE_DIR / "tests"
    if not test_dir.exists():
        print("[!] Test directory not found.")
        return
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir)]
    subprocess.run(cmd)

def show_audit_logs():
    step("Fetching recent Audit Trail logs from database...")
    db_path = BASE_DIR / "panchayat.db"
    if not db_path.exists():
        print("[!] Database not yet initialized.")
        return
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.complaint_id, a.actor_role, a.action, a.new_state, a.justification, a.created_at
        FROM complaint_audit_logs a
        ORDER BY a.created_at DESC LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No audit events recorded yet.")
        return
    for r in rows:
        print(f"[{r['created_at']}] Complaint #{r['complaint_id']} | {r['action']} by {r['actor_role']}: {r['justification']}")

def launch_server():
    step("Launching Gram Panchayat Portal Web Server...")
    print("\n" + "="*60)
    print("  Portal is running at: http://127.0.0.1:5000")
    print("  Press Ctrl + C in this terminal to stop the server.")
    print("="*60 + "\n")
    try:
        from app import app
        app.run(host="127.0.0.1", port=5000, debug=True)
    except Exception as e:
        print(f"[ERROR] Server failed to start: {e}")

def main():
    print_banner()
    check_and_install_dependencies()
    ensure_folders()
    initialize_database()

    print("\n" + "-"*50)
    print("  Choose an action:")
    print("   [1] Start Web Server (Default - http://127.0.0.1:5000)")
    print("   [2] Run Unit Tests")
    print("   [3] View Recent Audit Trail")
    print("   [4] Exit")
    print("-"*50)
    
    choice = input("Enter choice (1-4) [default: 1]: ").strip()
    if choice in ["", "1"]:
        launch_server()
    elif choice == "2":
        run_tests()
    elif choice == "3":
        show_audit_logs()
    else:
        print("Exiting builder agent. Have a productive day!")

if __name__ == "__main__":
    main()
