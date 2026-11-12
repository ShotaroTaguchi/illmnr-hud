"""SimHub: tyre overlay, 4 tiles colored by tread temperature, one per game.

    python simhub/build_tyres.py   ->  dist/simhub/<game>/ILLMNR_<GAME>_Tyres.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import BLUE, GREEN, PAD, RED, WHITE
from illmnr.game import Game, games
from illmnr.simhubdash import formula, gradient, layer, rect, text, vbar

# ---- tuning ----
# Tread temperature (deg C) -> tile color: blue (cold) -> green (ok) -> red (hot).
TYRE_COLD, TYRE_OK, TYRE_HOT = 40, 70, 100

SCALE = 0.75  # default overlay size relative to the 1x layout below
BODY, BAR, BAR_GAP = 84, 6, 2  # tile body width, wear bar width, space between them
TW, TH, GAP = BODY + BAR_GAP + BAR, 100, 8  # tile size (including the wear bar) and gap between tiles
W, H = 2 * TW + GAP + 2 * PAD, 2 * TH + GAP + 2 * PAD


def tyre_tile(g: Game, corner: str, x: int, y: int, bar_left: bool) -> list[dict]:
    """bar_left: put the wear bar on the left (outer side of the left-hand tyres)."""
    tread = g.get(f"tyre_tread.{corner}")
    carcass = g.get(f"tyre_carcass.{corner}")
    air = g.get(f"tyre_air.{corner}")
    pressure = g.get(f"tyre_pressure.{corner}")
    wear = g.get(f"tyre_left.{corner}")
    # "C 85  A 60" (carcass / air), only the parts the game has
    parts = [(k, v) for k, v in (("C", carcass), ("A", air)) if v]
    sub = " + ".join(f"'{'  ' if i else ''}{k} ' + format({v}, '0')" for i, (k, v) in enumerate(parts))
    p = f"tyre.{corner}"
    w = BODY
    band = 28   # dark band at the bottom for the pressure
    bar_x = x if bar_left else x + BODY + BAR_GAP
    x = x + BAR + BAR_GAP if bar_left else x  # tile body
    return [
        rect(f"{p}.bg", x, y, w, TH, GREEN, radius=6,
             bindings=[gradient("BackgroundColor", tread,
                                [(TYRE_COLD, BLUE), (TYRE_OK, GREEN), (TYRE_HOT, RED)])] if tread else []),
        # only the bottom corners are rounded, so the band sits flush inside the tile
        rect(f"{p}.shade", x, y + TH - band, w, band, "#59000000", radius=(0, 0, 6, 6)),
        text(f"{p}.name", x + 4, y + 2, 30, 14, corner, size=10, color="#CCFFFFFF", bold=True, align="left"),
        text(f"{p}.tread", x, y + 16, w, 38, "0" if tread else "--", size=30, bold=True,
             bindings=[formula("Text", tread, "0")] if tread else []),
        text(f"{p}.sub", x, y + 54, w, 14, "", size=10, color="#E6FFFFFF",
             bindings=[formula("Text", sub)] if sub else []),
        text(f"{p}.pressure", x, y + TH - band, w, band, "" if pressure else "--", size=13, bold=True,
             bindings=[formula("Text", f"format({pressure}, '0.0') + ' {g.pressure_unit}'")] if pressure else []),
        # remaining tread: thin bar on the outer side, full = new tyre
        vbar(f"{p}.wear", bar_x, y, BAR, TH, WHITE, bindings=[formula("Value", wear)] if wear else []),
    ]


def tyre_panel(g: Game, x0: int, y0: int) -> dict:
    items = []
    for corner, col, row in [("FL", 0, 0), ("FR", 1, 0), ("RL", 0, 1), ("RR", 1, 1)]:
        items += tyre_tile(g, corner, x0 + col * (TW + GAP), y0 + row * (TH + GAP), bar_left=col == 0)
    return layer("Tyres", items, x0, y0, 2 * TW + GAP, 2 * TH + GAP)


if __name__ == "__main__":
    for g in games():
        g.build("Tyres", "Tyre temperatures, pressures and wear", W, H, [tyre_panel(g, PAD, PAD)], sx=SCALE)
