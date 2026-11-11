"""Build every ILLMNR-HUD target, plus the RBRHUD release zip.

    .venv/Scripts/python build.py
"""
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = sorted(ROOT.glob("simhub/*/build_*.py")) + sorted(ROOT.glob("rbrhud/build_*.py"))

for script in SCRIPTS:
    subprocess.run([sys.executable, str(script)], check=True)

# RBRHUD release: files are stored as Plugins/RBRHUD/OverlayElements/..., so users just extract the zip
# into their RBR folder (the usual way RBR mods are installed).
elements = ROOT / "dist" / "rbrhud" / "OverlayElements"
release = ROOT / "dist" / "rbrhud" / "ILLMNR-HUD_RBRHUD.zip"
with zipfile.ZipFile(release, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(p for p in elements.rglob("*") if p.is_file()):
        info = zipfile.ZipInfo(f"Plugins/RBRHUD/{f.relative_to(elements.parent).as_posix()}",
                               date_time=(2020, 1, 1, 0, 0, 0))  # fixed time: byte-identical rebuilds
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 0  # as on Windows, so Linux builds match too
        z.writestr(info, f.read_bytes())
print(f"wrote {release}")
