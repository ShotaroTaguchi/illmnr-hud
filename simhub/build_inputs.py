"""SimHub: driver input overlay (steering wheel + pedals), one per game.

    python simhub/build_inputs.py   ->  dist/simhub/<game>/ILLMNR_<GAME>_Inputs.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import (BLUE, DIM, GREEN, INPUTS_H, INPUTS_W, ORANGE, PAD, PANEL,
                           PEDAL_GAP, PEDAL_H, PEDAL_W, PEDAL_X0, PEDAL_Y0, RED, TRACK, WHEEL_CX, WHEEL_CY, WHEEL_D)
from illmnr.game import Game, games
from illmnr.simhubdash import ellipse, formula, layer, rect, text, vbar

# ---- tuning ----
STEER_LOCK_DEG = 540   # displayed wheel rotation lock-to-lock (input -1..1 -> -270..+270 deg)
STEER_SIGN = 1         # set to -1 if the wheel turns the wrong way
PEDALS = [             # (label, value key (illmnr.game), color)
    ("CLU", "clutch", BLUE),
    ("BRK", "brake", RED),
    ("THR", "throttle", GREEN),
    ("HB", "handbrake", ORANGE),
]

W, H = INPUTS_W + 2 * PAD, INPUTS_H + 2 * PAD
RIM = "#FFE6EBF0"
HUB = "#FF000000"


def steering_wheel(g: Game, cx: float, cy: float, d: float) -> dict:
    steer = g.get("steer")  # None: the wheel stays straight and the angle shows "--"
    rot = f"{steer} * {STEER_LOCK_DEG / 2 * STEER_SIGN}" if steer else None
    r = d / 2
    items = [
        # every rotating part is centered on (cx, cy), so rotating around its own center = wheel center
        rect("wheel.spoke.h", cx - r + 4, cy - 4, d - 8, 8, RIM, radius=3, rotation=rot),
        # lower spoke: full-height box, only the bottom border (= lower half) is drawn
        rect("wheel.spoke.v", cx - 4, cy - r + 4, 8, d - 8, border=(0, int(r - 4), 0, 0),
             border_color=RIM, rotation=rot),
        ellipse("wheel.rim", cx - r, cy - r, d, d, RIM, thickness=9),
        # 12 o'clock marker: full-height box, only the top border is drawn
        rect("wheel.marker", cx - 5, cy - r, 10, d, border=(10, 0, 0, 0), border_color=ORANGE, rotation=rot),
        ellipse("wheel.hub", cx - 23, cy - 23, 46, 46, RIM, thickness=2, fill=HUB),
        text("wheel.gear", cx - 23, cy - 25, 46, 46, "N", size=30, bold=True,
             bindings=[formula("Text", g.get("gear"))]),
        text("wheel.steer", cx - 40, cy + r + 4, 80, 18, "" if steer else "--", size=12, color=DIM,
             bindings=[formula("Text", f"if({steer} < -0.005, 'L ', if({steer} > 0.005, 'R ', '')) "
                                       f"+ format(abs({steer}) * 100, '0') + '%'")] if steer else []),
    ]
    return layer("Wheel", items, cx - r, cy - r, d, d + 26)


def pedals(g: Game, x0: float, y0: float) -> dict:
    bw, gap, bh = PEDAL_W, PEDAL_GAP, PEDAL_H
    items = []
    for i, (label, field, color) in enumerate(PEDALS):
        x = x0 + i * (bw + gap)
        value = g.get(field)
        items += [
            vbar(f"pedal.{field}", x, y0, bw, bh, color, back=TRACK,
                 bindings=[formula("Value", value)] if value else []),
            text(f"pedal.{field}.pct", x - 8, y0 + bh + 2, bw + 16, 16, "0" if value else "--", size=12, bold=True,
                 bindings=[formula("Text", value, "0")] if value else []),
            text(f"pedal.{field}.label", x - 8, y0 + bh + 18, bw + 16, 14, label, size=10, color=DIM),
        ]
    return layer("Pedals", items, x0, y0, len(PEDALS) * (bw + gap) - gap, bh + 32)


if __name__ == "__main__":
    for g in games():
        g.build("Inputs", "Steering wheel and pedal inputs", W, H, [
            rect("bg", PAD, PAD, W - 2 * PAD, H - 2 * PAD, PANEL, radius=8),
            steering_wheel(g, cx=PAD + WHEEL_CX, cy=PAD + WHEEL_CY, d=WHEEL_D),
            pedals(g, x0=PAD + PEDAL_X0, y0=PAD + PEDAL_Y0),
        ])
