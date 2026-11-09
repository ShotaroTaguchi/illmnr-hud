"""Build the RBR (NGP UDP) tyre overlay: 4 tiles colored by tread temperature.

    python tools/build_rbr_tyres.py   ->  dist/RBR_Tyres.simhubdash
"""
from rbr_common import BLUE, GREEN, PAD, RAW, RED, WHITE, build, c_of
from simhubdash import formula, gradient, layer, rect, text, vbar

# ---- tuning ----
# Tread temperature (deg C) -> tile color: blue (cold) -> green (ok) -> red (hot).
TYRE_COLD, TYRE_OK, TYRE_HOT = 40, 70, 100

SCALE = 0.75  # default overlay size relative to the 1x layout below
BODY, BAR, BAR_GAP = 84, 6, 2  # tile body width, wear bar width, space between them
TW, TH, GAP = BODY + BAR_GAP + BAR, 100, 8  # tile size (including the wear bar) and gap between tiles
W, H = 2 * TW + GAP + 2 * PAD, 2 * TH + GAP + 2 * PAD


def tyre_tile(corner: str, susp: str, x: int, y: int, bar_left: bool) -> list[dict]:
    """bar_left: put the wear bar on the left (outer side of the left-hand tyres)."""
    tire = f"[{RAW}.car.{susp}.wheel.tire"
    tread = c_of(f"{tire}.treadTemperature]")
    carcass = c_of(f"{tire}.carcassTemperature]")
    air = c_of(f"{tire}.temperature]")
    wear = f"100 - 100 * ({' + '.join(f'{tire}.segment{i}.wear]' for i in range(1, 9))}) / 8"
    p = f"tyre.{corner}"
    w = BODY
    band = 28   # dark band at the bottom for the pressure
    bar_x = x if bar_left else x + BODY + BAR_GAP
    x = x + BAR + BAR_GAP if bar_left else x  # tile body
    return [
        rect(f"{p}.bg", x, y, w, TH, GREEN, radius=6,
             bindings=[gradient("BackgroundColor", tread,
                                [(TYRE_COLD, BLUE), (TYRE_OK, GREEN), (TYRE_HOT, RED)])]),
        # only the bottom corners are rounded, so the band sits flush inside the tile
        rect(f"{p}.shade", x, y + TH - band, w, band, "#59000000", radius=(0, 0, 6, 6)),
        text(f"{p}.name", x + 4, y + 2, 30, 14, corner, size=10, color="#CCFFFFFF", bold=True, align="left"),
        text(f"{p}.tread", x, y + 16, w, 38, "0", size=30, bold=True,
             bindings=[formula("Text", tread, "0")]),
        text(f"{p}.sub", x, y + 54, w, 14, "", size=10, color="#E6FFFFFF",
             bindings=[formula("Text", f"'C ' + format({carcass}, '0') + '  A ' + format({air}, '0')")]),
        text(f"{p}.pressure", x, y + TH - band, w, band, "", size=13, bold=True,
             bindings=[formula("Text", f"format({tire}.pressure] / 1000, '0.0') + ' kPa'")]),
        # remaining tread: thin bar on the outer side, full = new tyre
        vbar(f"{p}.wear", bar_x, y, BAR, TH, WHITE, bindings=[formula("Value", wear)]),
    ]


def tyre_panel(x0: int, y0: int) -> dict:
    items = []
    for corner, susp, col, row in [("FL", "suspensionLF", 0, 0), ("FR", "suspensionRF", 1, 0),
                                   ("RL", "suspensionLB", 0, 1), ("RR", "suspensionRB", 1, 1)]:
        items += tyre_tile(corner, susp, x0 + col * (TW + GAP), y0 + row * (TH + GAP), bar_left=col == 0)
    return layer("Tyres", items, x0, y0, 2 * TW + GAP, 2 * TH + GAP)


if __name__ == "__main__":
    build("RBR_Tyres", "RBR Tyres",
          "Tyre temperatures, pressures and wear for Richard Burns Rally (NGP UDP telemetry)",
          W, H, [tyre_panel(PAD, PAD)], sx=SCALE)
