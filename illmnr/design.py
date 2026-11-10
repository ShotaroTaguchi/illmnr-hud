"""ILLMNR-HUD design: palette and shared layout. Used by every target (SimHub, RBRHUD, ...)."""

PREFIX = "ILLMNR"  # illuminer: every overlay / element name starts with this (keeps them apart from others)
AUTHOR = "ShotaroTaguchi"  # GitHub account, so the dashboards can be traced back to this repo

# ---- colors (#AARRGGBB, SimHub format; RBRHUD uses hud()) ----
PANEL = "#FF000000"  # opaque black so in-car gauges underneath don't show through
WHITE = "#FFFFFFFF"
DIM = "#FF9AA4AE"
TRACK = "#40FFFFFF"  # empty part of bars
BLUE = "#FF2F7DE1"
GREEN = "#FF2DBE5A"
YELLOW = "#FFFFC800"
ORANGE = "#FFFF6A00"
RED = "#FFE8202A"

PAD = 8  # margin around a panel inside its overlay

# ---- Engine panel (1x layout; targets scale it) ----
ENGINE_W, ENGINE_H = 400, 114  # panel size
ENGINE_SIDE = 12               # inner margin of the left / right blocks
# Shift lights: (RPM percent threshold, color)
SHIFT_LIGHTS = [
    (55, GREEN), (60, GREEN), (65, GREEN),
    (70, YELLOW), (75, YELLOW), (80, YELLOW),
    (84, ORANGE), (88, ORANGE),
    (92, RED), (95, RED),
]

# ---- Inputs panel (1x, measured from the panel's top-left; SimHub adds PAD around it) ----
INPUTS_W, INPUTS_H = 294, 134
WHEEL_CX, WHEEL_CY, WHEEL_D = 72, 62, 108       # wheel center and diameter
PEDAL_X0, PEDAL_Y0 = 158, 10                    # top-left of the first pedal bar
PEDAL_W, PEDAL_GAP, PEDAL_H = 22, 14, 90

# ---- Small panels: Time / Delta / Stage (1x) ----
SMALL_W, SMALL_H = 184, 66


def hud(color: str) -> str:
    """'#AARRGGBB' -> RBRHUD 'aarrggbb'."""
    return color.lstrip("#").lower()
