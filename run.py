#!/usr/bin/env python3
"""
run.py — MAon-DAExt Linked Art Toolkit launcher

• Checks Python version (3.10+ required)
• Installs dependencies if missing
• Starts the Flask server
• Opens http://localhost:5050 in your browser
"""

import sys, subprocess, webbrowser, time, os

MIN_PYTHON = (3, 10)

def main():
    # ── Version check ──────────────────────────────────────────
    if sys.version_info < MIN_PYTHON:
        print(f"✗  Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required "
              f"(you have {sys.version_info.major}.{sys.version_info.minor}).")
        sys.exit(1)

    # ── Install dependencies ───────────────────────────────────
    required = ["rdflib", "flask"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Installing missing packages: {', '.join(missing)} …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing, "-q"])
        print("Dependencies installed.\n")

    # ── Launch server ──────────────────────────────────────────
    url = "http://localhost:5050"
    print("Starting MAon-DAExt → Linked Art converter …")
    print(f"  Open {url} in your browser (opening automatically in 2 s)\n")
    print("  Press Ctrl+C to stop.\n")

    # Open browser after short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask (same process)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from app import app
    app.run(debug=False, port=5050)

if __name__ == "__main__":
    main()
