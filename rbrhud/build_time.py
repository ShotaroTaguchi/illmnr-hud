"""RBRHUD / RBR: Time and Delta elements (same look and size as the SimHub ones).

    .venv/Scripts/python rbrhud/build_time.py   ->  ILLMNR_Time.element, ILLMNR_Delta.element (+ textures)

Delta uses RBRHUD's own delta timer (DeltaTime), not SimHub's best lap.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import DIM, GREEN, RED, SMALL_H, SMALL_W, TRACK, WHITE, hud
from illmnr.rbrhud import FONT_BOLD, Element

S = 1.2                # same default size as the SimHub Time / Delta
DELTA_BAR_RANGE = 10.0  # seconds at which the delta bar reaches the end
PW, PH = SMALL_W, SMALL_H  # panel (1x), shared with simhub/build_time.py


def panel(name: str, label: str) -> Element:
    el = Element(name, S, fonts={"NumBold": (FONT_BOLD, 32)})
    el.tex_rect("Panel", PW, PH, radius=8, fill=(0, 0, 0, 255))
    el.tex_text("Label", label, 10, 80, 14, bold=True, align="left")
    el.placed("panel", "Static", 0, 0, WHITE, texture="Panel")
    el.placed("label", "Static", 10, 4, DIM, texture="Label")
    return el


def time() -> None:
    el = panel("Time", "TIME")
    el.number("value", "RaceTime", "NumBold", 32, PW / 2, 14, 46, fmt="TimeMinSecM", justification="Center")
    el.write("ILLMNR RBR Time")


def delta() -> None:
    el = panel("Delta", "DELTA")
    # slower than the reference (DeltaTime > 0) -> red, as RBRHUD's own "deltabadgored" effect
    el.add("slower", type="Effect", effecttype="ColourChange|", data="DeltaTime", threshold=0.001,
           newcolour=hud(RED))
    el.number("value", "DeltaTime", "NumBold", 32, PW / 2, 12, 40, colour=GREEN, fmt="Decimal2",
              justification="Center", effect="slower")

    # bar: faster -> green grows right from the center, slower -> red grows left
    bx, by, bw, bh = 12, PH - 12, PW - 24, 5
    half = bw / 2
    el.tex_rect("Track", bw, bh, radius=2)
    el.tex_rect("Half", half, bh, radius=2)
    el.tex_rect("Center", 2, bh + 6)
    el.placed("track", "Static", bx, by, TRACK, texture="Track")
    common = dict(texture="Half", data="DeltaTime", expandmap0value=0.0, expandmap0expand=0.0, expandmap1expand=1.0)
    el.placed("faster", "Expanding", bx + half, by, GREEN, **common, expandmap1value=-DELTA_BAR_RANGE,
              direction="right")
    el.placed("slower_bar", "Expanding", bx, by, RED, **common, expandmap1value=DELTA_BAR_RANGE, direction="left")
    el.placed("center", "Static", bx + half - 1, by - 3, WHITE, texture="Center")
    el.write("ILLMNR RBR Delta")


if __name__ == "__main__":
    time()
    delta()
