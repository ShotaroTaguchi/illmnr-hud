"""RBRHUD / RBR: engine element (works in replays, unlike the SimHub overlay).

    .venv/Scripts/python rbrhud/build_engine.py
      -> dist/rbrhud/OverlayElements/{Custom/ILLMNR_Engine.element, textures/ILLMNR_Engine.png + .ini}

Same layout as simhub/rbr/build_engine.py (illmnr.design). Needs Pillow (requirements.txt).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import DIM, ENGINE_H as PH, ENGINE_SIDE as SIDE, ENGINE_W as PW, RED, SHIFT_LIGHTS, WHITE, hud
from illmnr.rbrhud import FONT_BOLD, FONT_REG, Element

S = 1.5  # pixel scale of the 1x layout (same default size as the SimHub overlay)


def main() -> None:
    el = Element("Engine", S, fonts={"NumBold": (FONT_BOLD, 34), "Num": (FONT_REG, 18)})
    el.tex_rect("Panel", PW, PH, radius=8, fill=(0, 0, 0, 255))
    el.tex_rect("Led", 22, 10, radius=2)
    gears = ["GearR", "GearN"] + [f"Gear{i}" for i in range(1, 8)]  # RBR gear index 0=R, 1=N, 2=1st ...
    for key in gears:
        el.tex_text(key, key[4:], 84, 90, 96, bold=True)
    for key, label in [("LabelWater", "WATER"), ("LabelRadWater", "RAD WATER"), ("LabelOil", "OIL")]:
        el.tex_text(key, label, 12, 74, 20, align="left")
    el.tex_text("UnitKmh", "km/h", 11, 34, 20, align="left")
    el.tex_text("UnitRpm", "rpm", 11, 34, 20, align="left")
    el.tex_text("UnitC", "°C", 11, 20, 20, align="left")

    # effects
    el.add("upshift", type="Effect", effecttype="Blink|ColourChange|", data="UpShift",
           blinkspeed=150.0, newcolour=hud(RED))
    el.add("coolanthot", type="Effect", effecttype="ColourChange|", data="CoolantTemperatureWarning",
           newcolour=hud(RED))
    el.add("oilhot", type="Effect", effecttype="ColourChange|", data="OilTemperatureWarning", newcolour=hud(RED))

    el.placed("panel", "Static", 0, 0, WHITE, texture="Panel")

    # shift lights: each shows from its RPM percent upwards
    lw, gap = 22, 4
    lx = (PW - (len(SHIFT_LIGHTS) * (lw + gap) - gap)) / 2
    for i, (threshold, colour) in enumerate(SHIFT_LIGHTS):
        el.placed(f"shift{i + 1}", "Simple", lx + i * (lw + gap), 8, colour, texture="Led",
                  data="RPMPercent", effect="upshift", rangemin=float(threshold), rangemax=1000.0)

    for idx, key in enumerate(gears):
        el.placed(f"gear_{key.lower()}", "Simple", PW / 2 - 45, 18, WHITE, texture=key, data="Gear", equal=idx)

    # right block: speed + rpm (numbers right-aligned at the value box's right edge)
    rx = PW - SIDE - 36 - 84
    el.number("speed", "SpeedKPH", "NumBold", 34, rx + 84, 30, 40)
    el.placed("speed_unit", "Static", rx + 86, 44, DIM, texture="UnitKmh")
    el.number("rpm", "RPM", "Num", 18, rx + 84, 70, 24)
    el.placed("rpm_unit", "Static", rx + 86, 74, DIM, texture="UnitRpm")

    # left block: temperatures
    temps = [("water", "LabelWater", "CoolantTemperatureC", "coolanthot"),
             ("radwater", "LabelRadWater", "RadiatorCoolantTemperatureC", None),
             ("oil", "LabelOil", "OilTemperatureC", "oilhot")]
    for i, (key, label, data, effect) in enumerate(temps):
        y = 34 + i * 22
        el.placed(f"{key}_label", "Static", SIDE, y, DIM, texture=label)
        el.number(key, data, "NumBold", 15, SIDE + 112, y, 20, **({"effect": effect} if effect else {}))
        el.placed(f"{key}_unit", "Static", SIDE + 114, y, DIM, texture="UnitC")

    el.write("ILLMNR RBR Engine")


if __name__ == "__main__":
    main()
