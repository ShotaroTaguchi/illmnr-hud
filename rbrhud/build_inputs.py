"""RBRHUD / RBR: Inputs element (steering wheel + pedals), same look as the SimHub one.

    .venv/Scripts/python rbrhud/build_inputs.py   ->  ILLMNR_Inputs.element (+ textures)

The wheel turns by the real wheel angle (InputSteeringDeg), as RBRHUD's own InputDisplay does.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import (BLUE, DIM, GREEN, INPUTS_H, INPUTS_W, ORANGE, PEDAL_GAP, PEDAL_H, PEDAL_W, PEDAL_X0,
                           PEDAL_Y0, RED, TRACK, WHEEL_CX, WHEEL_CY, WHEEL_D, WHITE)
from illmnr.rbrhud import FONT_BOLD, Element

S = 1.0
PW, PH = INPUTS_W, INPUTS_H  # panel-relative layout shared with simhub/build_inputs.py
CX, CY = WHEEL_CX, WHEEL_CY
PEDALS = [("CLU", "InputClutchProcessed", BLUE), ("BRK", "InputBrakeProcessed", RED),
          ("THR", "InputThrottleProcessed", GREEN), ("HB", "InputHandbrakeProcessed", ORANGE)]
RIM = (230, 235, 240, 255)
SS = 4  # supersampling for the wheel drawing


def wheel_image(el: Element) -> Image.Image:
    """Rim, spokes, 12 o'clock marker and hub in one texture (rotated as a whole)."""
    d = el.px(WHEEL_D) * SS
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    r, t = d / 2, 9 * SS * el.s
    g.rounded_rectangle([t, r - 4 * SS, d - t, r + 4 * SS], radius=3 * SS, fill=RIM)     # horizontal spoke
    g.rectangle([r - 4 * SS, r, r + 4 * SS, d - t], fill=RIM)                             # lower spoke
    g.ellipse([0, 0, d - 1, d - 1], outline=RIM, width=round(t))                          # rim
    g.rectangle([r - 5 * SS, 0, r + 5 * SS, t + 1 * SS], fill=(255, 106, 0, 255))         # 12 o'clock marker
    hub = 23 * SS
    g.ellipse([r - hub, r - hub, r + hub, r + hub], fill=(0, 0, 0, 255), outline=RIM, width=2 * SS)
    return im.resize((el.px(WHEEL_D), el.px(WHEEL_D)), Image.LANCZOS)


def main() -> None:
    el = Element("Inputs", S, fonts={"NumBold": (FONT_BOLD, 30)})
    el.tex_rect("Panel", PW, PH, radius=8, fill=(0, 0, 0, 255))
    el.tex_image("Wheel", wheel_image(el))
    gears = ["GearR", "GearN"] + [f"Gear{i}" for i in range(1, 8)]  # RBR gear index 0=R, 1=N, 2=1st ...
    for key in gears:
        el.tex_text(key, key[4:], 30, 46, 46, bold=True)

    bw, gap, bh, x0, y0 = PEDAL_W, PEDAL_GAP, PEDAL_H, PEDAL_X0, PEDAL_Y0
    el.tex_rect("Bar", bw, bh)
    for label, _, _ in PEDALS:
        el.tex_text(f"L{label}", label, 10, bw + 16, 14, align="center")

    el.placed("panel", "Static", 0, 0, WHITE, texture="Panel")
    # Rotating elements are positioned by their center
    el.placed("wheel", "Rotating", CX, CY, WHITE, texture="Wheel", data="InputSteeringDeg", digital=1,
              rotation0deg=-1800.0, rotation0value=-1800.0, rotation1deg=1800.0, rotation1value=1800.0)
    for idx, key in enumerate(gears):
        el.placed(f"gear_{key.lower()}", "Simple", CX - 23, CY - 25, WHITE, texture=key, data="Gear", equal=idx)

    for i, (label, data, colour) in enumerate(PEDALS):
        x = x0 + i * (bw + gap)
        el.placed(f"track_{label.lower()}", "Static", x, y0, TRACK, texture="Bar")
        el.placed(f"bar_{label.lower()}", "Expanding", x, y0, colour, texture="Bar", data=data,
                  expandmap0value=0.0, expandmap0expand=0.0, expandmap1value=1.0, expandmap1expand=1.0,
                  direction="up")
        el.number(f"pct_{label.lower()}", data, "NumBold", 12, x + bw / 2, y0 + bh + 2, 16, fmt="Percentage",
                  justification="Center")
        el.placed(f"label_{label.lower()}", "Static", x - 8, y0 + bh + 18, DIM, texture=f"L{label}")

    el.write("ILLMNR RBR Inputs")


if __name__ == "__main__":
    main()
