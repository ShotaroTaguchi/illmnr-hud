"""Richard Burns Rally (NGP UDP telemetry) for the SimHub target: property names and the build helper."""
from pathlib import Path

from illmnr.design import AUTHOR
from illmnr.simhubdash import dashboard, scale, write_simhubdash

DIST = Path(__file__).resolve().parent.parent / "dist" / "simhub" / "rbr"

RAW = "GameRawData.NGPTelemetry"  # NGP packet as exposed by SimHub
GD = "DataCorePlugin.GameData.NewData"
K = 273.15  # NGP temperatures are Kelvin


def c_of(expr_kelvin: str) -> str:
    """Kelvin expression -> Celsius expression."""
    return f"({expr_kelvin}) - {K}"


def build(name: str, title: str, description: str, width: int, height: int, items: list[dict],
          sx: float = 1.0, sy: float | None = None) -> None:
    """Write dist/simhub/rbr/<name>.simhubdash. Layouts are written at 1x; sx/sy set the default size."""
    sy = sx if sy is None else sy
    scale(items, sx, sy)
    dash, meta = dashboard(title=title, description=description, author=AUTHOR,
                           width=round(width * sx), height=round(height * sy), items=items)
    print(f"wrote {write_simhubdash(dash, meta, name, DIST)}")
