"""SimHub: brake overlay. 4 tiles colored by brake disc temperature (same look as Tyres), one per game.

    python simhub/build_brakes.py   ->  dist/simhub/<game>/ILLMNR_<GAME>_Brakes.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import BLUE, GREEN, PAD, RED, WHITE
from illmnr.game import Game, games
from illmnr.simhubdash import formula, gradient, layer, rect, text, vbar

# ---- tuning ----
# Disc temperature (deg C) -> tile color: blue (cold) -> green (working range) -> red (overheating).
# First guess for rally brakes; adjust after watching a few stages.
BRAKE_COLD, BRAKE_OK, BRAKE_HOT = 150, 350, 650

SCALE = 0.75
BODY, BAR, BAR_GAP = 84, 6, 2
TW, TH, GAP = BODY + BAR_GAP + BAR, 70, 8  # shorter than Tyres: one big number per tile
W, H = 2 * TW + GAP + 2 * PAD, 2 * TH + GAP + 2 * PAD


def brake_tile(g: Game, corner: str, x: int, y: int, bar_left: bool) -> list[dict]:
    temp = g.get(f"brake_temp.{corner}")
    remaining = g.get(f"brake_left.{corner}")
    p = f"brake.{corner}"
    bar_x = x if bar_left else x + BODY + BAR_GAP
    x = x + BAR + BAR_GAP if bar_left else x
    return [
        rect(f"{p}.bg", x, y, BODY, TH, GREEN, radius=6,
             bindings=[gradient("BackgroundColor", temp, [(BRAKE_COLD, BLUE), (BRAKE_OK, GREEN), (BRAKE_HOT, RED)])]
             if temp else []),
        text(f"{p}.name", x + 4, y + 2, 30, 14, corner, size=10, color="#CCFFFFFF", bold=True, align="left"),
        text(f"{p}.temp", x, y + 16, BODY, 38, "0" if temp else "--", size=28, bold=True,
             bindings=[formula("Text", temp, "0")] if temp else []),
        text(f"{p}.unit", x, y + TH - 18, BODY, 14, "°C", size=10, color="#E6FFFFFF"),
        vbar(f"{p}.wear", bar_x, y, BAR, TH, WHITE, bindings=[formula("Value", remaining)] if remaining else []),
    ]


def brake_panel(g: Game, x0: int, y0: int) -> dict:
    items = []
    for corner, col, row in [("FL", 0, 0), ("FR", 1, 0), ("RL", 0, 1), ("RR", 1, 1)]:
        items += brake_tile(g, corner, x0 + col * (TW + GAP), y0 + row * (TH + GAP), bar_left=col == 0)
    return layer("Brakes", items, x0, y0, 2 * TW + GAP, 2 * TH + GAP)


if __name__ == "__main__":
    for g in games():
        g.build("Brakes", "Brake disc temperatures and wear", W, H, [brake_panel(g, PAD, PAD)], sx=SCALE)
