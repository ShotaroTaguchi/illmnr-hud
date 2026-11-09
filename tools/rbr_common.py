"""Shared look and property names for the RBR overlays."""
from pathlib import Path

from simhubdash import dashboard, scale, write_simhubdash

DIST = Path(__file__).resolve().parent.parent / "dist"

RAW = "GameRawData.NGPTelemetry"  # NGP packet as exposed by SimHub
GD = "DataCorePlugin.GameData.NewData"
K = 273.15  # NGP temperatures are Kelvin

# ---- colors (#AARRGGBB) ----
PANEL = "#FF101418"  # opaque so in-car gauges underneath don't show through
WHITE = "#FFFFFFFF"
DIM = "#FF9AA4AE"
TRACK = "#40FFFFFF"  # empty part of bars
BLUE = "#FF2F7DE1"
GREEN = "#FF2DBE5A"
YELLOW = "#FFFFC800"
ORANGE = "#FFFF6A00"
RED = "#FFE8202A"

PAD = 8
AUTHOR = "Shotaro T"


def c_of(expr_kelvin: str) -> str:
    """Kelvin expression -> Celsius expression."""
    return f"({expr_kelvin}) - {K}"


def build(name: str, title: str, description: str, width: int, height: int, items: list[dict],
          sx: float = 1.0, sy: float | None = None) -> None:
    """Write dist/<name>.simhubdash. Layouts are written at 1x; sx/sy set the default overlay size."""
    sy = sx if sy is None else sy
    scale(items, sx, sy)
    dash, meta = dashboard(title=title, description=description, author=AUTHOR,
                           width=round(width * sx), height=round(height * sy), items=items)
    print(f"wrote {write_simhubdash(dash, meta, name, DIST)}")
