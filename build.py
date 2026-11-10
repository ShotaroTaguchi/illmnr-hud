"""Build every ILLMNR-HUD target.

    .venv/Scripts/python build.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = sorted(ROOT.glob("simhub/*/build_*.py")) + sorted(ROOT.glob("rbrhud/build_*.py"))

for script in SCRIPTS:
    subprocess.run([sys.executable, str(script)], check=True)
