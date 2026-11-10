"""ILLMNR-HUD design: palette and shared layout. Used by every target (SimHub, RBRHUD, ...)."""

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


def hud(color: str) -> str:
    """'#AARRGGBB' -> RBRHUD 'aarrggbb'."""
    return color.lstrip("#").lower()
