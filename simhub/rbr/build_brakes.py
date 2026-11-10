"""SimHub / RBR: brake overlay. 4 tiles colored by brake disc temperature (same look as Tyres).

    python simhub/rbr/build_brakes.py   ->  dist/simhub/rbr/ILLMNR_RBR_Brakes.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for the illmnr package

from illmnr.design import BLUE, GREEN, PAD, RED, WHITE
from illmnr.rbr import RAW, build, c_of
from illmnr.simhubdash import formula, gradient, layer, rect, text, vbar

# ---- tuning ----
# Disc temperature (deg C) -> tile color: blue (cold) -> green (working range) -> red (overheating).
# First guess for rally brakes; adjust after watching a few stages.
BRAKE_COLD, BRAKE_OK, BRAKE_HOT = 150, 350, 650

SCALE = 0.75
BODY, BAR, BAR_GAP = 84, 6, 2
TW, TH, GAP = BODY + BAR_GAP + BAR, 70, 8  # shorter than Tyres: one big number per tile
W, H = 2 * TW + GAP + 2 * PAD, 2 * TH + GAP + 2 * PAD


def brake_tile(corner: str, susp: str, x: int, y: int, bar_left: bool) -> list[dict]:
    disc = f"[{RAW}.car.{susp}.wheel.brakeDisk"
    temp = c_of(f"{disc}.temperature]")
    remaining = f"100 - 100 * {disc}.wear]"  # wear assumed 0 = new .. 1 = worn out (not verified yet)
    p = f"brake.{corner}"
    bar_x = x if bar_left else x + BODY + BAR_GAP
    x = x + BAR + BAR_GAP if bar_left else x
    return [
        rect(f"{p}.bg", x, y, BODY, TH, GREEN, radius=6,
             bindings=[gradient("BackgroundColor", temp, [(BRAKE_COLD, BLUE), (BRAKE_OK, GREEN), (BRAKE_HOT, RED)])]),
        text(f"{p}.name", x + 4, y + 2, 30, 14, corner, size=10, color="#CCFFFFFF", bold=True, align="left"),
        text(f"{p}.temp", x, y + 16, BODY, 38, "0", size=28, bold=True, bindings=[formula("Text", temp, "0")]),
        text(f"{p}.unit", x, y + TH - 18, BODY, 14, "°C", size=10, color="#E6FFFFFF"),
        vbar(f"{p}.wear", bar_x, y, BAR, TH, WHITE, bindings=[formula("Value", remaining)]),
    ]


def brake_panel(x0: int, y0: int) -> dict:
    items = []
    for corner, susp, col, row in [("FL", "suspensionLF", 0, 0), ("FR", "suspensionRF", 1, 0),
                                   ("RL", "suspensionLB", 0, 1), ("RR", "suspensionRB", 1, 1)]:
        items += brake_tile(corner, susp, x0 + col * (TW + GAP), y0 + row * (TH + GAP), bar_left=col == 0)
    return layer("Brakes", items, x0, y0, 2 * TW + GAP, 2 * TH + GAP)


if __name__ == "__main__":
    build("RBR_Brakes", "RBR Brakes",
          "Brake disc temperatures and wear for Richard Burns Rally (NGP UDP telemetry)",
          W, H, [brake_panel(PAD, PAD)], sx=SCALE)
