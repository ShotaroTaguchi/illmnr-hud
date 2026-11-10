"""SimHub / RBR: engine overlay (shift lights, gear, speed, rpm, temperatures).

    python simhub/rbr/build_engine.py   ->  dist/simhub/rbr/RBR_Engine.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for the illmnr package

from illmnr.design import (BLUE, DIM, ENGINE_H as PH, ENGINE_SIDE as SIDE, ENGINE_W as PW, PAD, PANEL, RED,
                           SHIFT_LIGHTS, WHITE)
from illmnr.rbr import GD, RAW, build, c_of
from illmnr.simhubdash import formula, gradient, layer, rect, text

# ---- tuning ----
# Temperature (deg C) -> text color: blue (cold, OK - 30) -> white (OK) -> red (HOT).
WATER_OK, WATER_HOT = 90, 110
OIL_OK, OIL_HOT = 110, 130  # oil runs hotter than coolant; ~120 is normal
# Shift lights: illmnr.design.SHIFT_LIGHTS (SimHub's displayed RPM %, per-car redline)

#  ┌────────────── shift lights ──────────────┐
#  │ WATER     80°C              57 km/h      │
#  │ RAD WATER 51°C      2     1957 rpm       │
#  │ OIL       91°C                           │
#  └──────────────────────────────────────────┘
SCALE_X, SCALE_Y = 1.5, 1.6  # default overlay size relative to the 1x layout (illmnr.design.ENGINE_*)
W, H = PW + 2 * PAD, PH + 2 * PAD


def engine_panel(x0: int, y0: int) -> dict:
    items = [rect("engine.bg", x0, y0, PW, PH, PANEL, radius=8)]
    cx = x0 + PW // 2

    # shift lights row (top, centered)
    rpm_pct = f"[{GD}.CarSettings_CurrentDisplayedRPMPercent]"
    lw, gap = 22, 4
    row_w = len(SHIFT_LIGHTS) * (lw + gap) - gap
    lx = cx - row_w // 2
    for i, (threshold, color) in enumerate(SHIFT_LIGHTS):
        items.append(rect(f"engine.shift{i + 1}", lx + i * (lw + gap), y0 + 8, lw, 10, color, radius=2,
                          bindings=[formula("Visible", f"{rpm_pct} >= {threshold}")]))
    # redline: whole row blinks red
    items.append(rect("engine.redline", lx, y0 + 8, row_w, 10, RED, radius=2,
                      BlinkEnabled=True, BlinkDelay=80.0,
                      bindings=[formula("Visible", f"[{GD}.CarSettings_RPMRedLineReached]")]))

    # center: gear
    items.append(text("engine.gear", cx - 45, y0 + 18, 90, 96, "N", size=84, bold=True,
                      bindings=[formula("Text", f"[{GD}.Gear]")]))

    # right block: speed + rpm (value right-aligned, unit after it)
    rx = x0 + PW - SIDE - 36 - 84  # value box left edge (value 84px + unit 36px)
    items.append(text("engine.speed", rx, y0 + 30, 84, 40, "0", size=34, bold=True, align="right",
                      bindings=[formula("Text", f"[{GD}.SpeedKmh]", "0")]))
    items.append(text("engine.speed.unit", rx + 86, y0 + 44, 34, 20, "km/h", size=11, color=DIM, align="left"))
    items.append(text("engine.rpm", rx, y0 + 70, 84, 24, "0", size=18, align="right",
                      bindings=[formula("Text", f"[{GD}.Rpms]", "0")]))
    items.append(text("engine.rpm.unit", rx + 86, y0 + 74, 34, 20, "rpm", size=11, color=DIM, align="left"))

    # left block: temperatures, mirroring the right block
    # engineTemperature matches the in-car "Oil T" gauge, so it is shown as OIL
    temps = [
        ("water", "WATER", f"[{RAW}.car.engine.engineCoolantTemperature]", WATER_OK, WATER_HOT),
        ("radwater", "RAD WATER", f"[{RAW}.car.engine.radiatorCoolantTemperature]", WATER_OK, WATER_HOT),
        ("oil", "OIL", f"[{RAW}.car.engine.engineTemperature]", OIL_OK, OIL_HOT),
    ]
    lx0 = x0 + SIDE
    for i, (name, label, raw, ok, hot) in enumerate(temps):
        y = y0 + 34 + i * 22
        key = f"engine.{name}"
        items.append(text(f"{key}.label", lx0, y, 74, 20, label, size=12, color=DIM, align="left"))
        items.append(text(key, lx0 + 72, y, 40, 20, "0", size=15, bold=True, align="right",
                          bindings=[formula("Text", c_of(raw), "0"),
                                    gradient("TextColor", c_of(raw),
                                             [(ok - 30, BLUE), (ok, WHITE), (hot, RED)])]))
        items.append(text(f"{key}.unit", lx0 + 114, y, 20, 20, "°C", size=11, color=DIM, align="left"))

    return layer("Engine", items, x0, y0, PW, PH)


if __name__ == "__main__":
    build("RBR_Engine", "RBR Engine",
          "Shift lights, gear, speed, rpm and temperatures for Richard Burns Rally (NGP UDP telemetry)",
          W, H, [engine_panel(PAD, PAD)], sx=SCALE_X, sy=SCALE_Y)
