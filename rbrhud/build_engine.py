"""RBRHUD / RBR: engine element (works in replays, unlike the SimHub overlay).

    .venv/Scripts/python rbrhud/build_engine.py
      -> dist/rbrhud/OverlayElements/textures/ILLMNR_Engine.png + .ini   (texture atlas)
      -> dist/rbrhud/OverlayElements/Custom/ILLMNR_Engine.element         (element)

Copy dist/rbrhud/OverlayElements into  <RBR>/Plugins/RBRHUD/  and add
"Custom/ILLMNR_Engine.element" to an overlay with RBRHUD's in-game Overlay Editor.

Same layout as simhub/rbr/build_engine.py (illmnr.design). Needs Pillow (requirements.txt).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr import design
from illmnr.design import ENGINE_H as PH, ENGINE_SIDE as SIDE, ENGINE_W as PW, hud

ROOT = Path(__file__).resolve().parents[1] / "dist" / "rbrhud" / "OverlayElements"
NAME = f"{design.PREFIX}_Engine"
S = 1.5  # pixel scale of the 1x layout (same default size as the SimHub overlay)

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

# colors as RBRHUD AARRGGBB (lowercase, no #)
WHITE, DIM, RED = hud(design.WHITE), hud(design.DIM), hud(design.RED)
SHIFT_LIGHTS = [(threshold, hud(color)) for threshold, color in design.SHIFT_LIGHTS]

# Number elements use bitmap fonts embedded in this element's own atlas (an element can only use
# one atlas, so RBRHUD's built-in fonts such as Bahnschrift are not available here).
# (font name, ttf, size at 1x)
NUM_BOLD, NUM = f"{design.PREFIX}_NumBold", f"{design.PREFIX}_Num"
FONTS = {NUM_BOLD: (FONT_BOLD, 34), NUM: (FONT_REG, 18)}
FONT_CHARS = " 0123456789-.:%+"


def px(v: float) -> int:
    return round(v * S)


# ---------------------------------------------------------------- textures

def tex_panel() -> Image.Image:
    im = Image.new("RGBA", (px(PW), px(PH)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, px(PW) - 1, px(PH) - 1], radius=px(8), fill=(0, 0, 0, 255))
    return im


def tex_led() -> Image.Image:
    im = Image.new("RGBA", (px(22), px(10)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, px(22) - 1, px(10) - 1], radius=px(2), fill=(255, 255, 255, 255))
    return im


def tex_text(s: str, size: float, w: float, h: float, bold: bool = False, align: str = "center") -> Image.Image:
    """White text in a fixed-size cell (so every glyph of e.g. the gear sits at the same spot)."""
    font = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, px(size))
    im = Image.new("RGBA", (px(w), px(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    anchor = {"left": "lm", "center": "mm", "right": "rm"}[align]
    x = {"left": 0, "center": px(w) / 2, "right": px(w)}[align]
    d.text((x, px(h) / 2), s, font=font, fill=(255, 255, 255, 255), anchor=anchor)
    return im


def font_sheet(ttf: str, size: float) -> tuple[Image.Image, dict[int, tuple[int, int, int, int]], int]:
    """Render FONT_CHARS into one sheet. Returns (sheet, char code -> rect inside the sheet, line height)."""
    font = ImageFont.truetype(ttf, px(size))
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    pad, x = 4, 4
    glyphs = {}
    for ch in FONT_CHARS:
        w = max(1, round(font.getlength(ch)))  # advance width: digits share the same width (tabular)
        glyphs[ord(ch)] = (x, pad, w, line_h)
        x += w + pad
    sheet = Image.new("RGBA", (x, line_h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for ch in FONT_CHARS:
        gx, gy, _, _ = glyphs[ord(ch)]
        d.text((gx, gy + ascent), ch, font=font, fill=(255, 255, 255, 255), anchor="ls")
    return sheet, glyphs, line_h


def pow2(n: int) -> int:
    p = 1
    while p < n:
        p *= 2
    return p


def build_atlas(textures: dict[str, Image.Image], fonts: dict[str, tuple[Image.Image, dict]]) -> dict:
    """Shelf packer -> writes <NAME>.png / <NAME>.ini (power-of-two size, as RBRHUD's own atlases)."""
    width, pad = 1024, 4
    items = {**textures, **{f"__font__{n}": sheet for n, (sheet, _) in fonts.items()}}
    x = y = shelf = 0
    rects = {}
    for name, im in sorted(items.items(), key=lambda kv: -kv[1].height):
        if x + im.width + pad > width:
            x, y, shelf = 0, y + shelf + pad, 0
        rects[name] = (x, y, im.width, im.height)
        x += im.width + pad
        shelf = max(shelf, im.height)
    atlas = Image.new("RGBA", (width, pow2(y + shelf)), (0, 0, 0, 0))
    for name, (ax, ay, _, _) in rects.items():
        atlas.paste(items[name], (ax, ay))
    out = ROOT / "textures"
    out.mkdir(parents=True, exist_ok=True)
    atlas.save(out / f"{NAME}.png")
    lines = ["[MAIN]", f"texture=textures/{NAME}.png", "[Objects]"]
    lines += [f"{n}={x},{y},{w},{h}" for n, (x, y, w, h) in rects.items() if not n.startswith("__font__")]
    for fname, (_, glyphs) in fonts.items():
        cx, cy, cw, ch = rects[f"__font__{fname}"]
        lines += ["", f"[{fname}]", f"charset={cx},{cy},{cw},{ch}"]
        lines += [f"{code}={gx},{gy},{gw},{gh}" for code, (gx, gy, gw, gh) in glyphs.items()]
    (out / f"{NAME}.ini").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rects


# ---------------------------------------------------------------- element

def section(name: str, **kv) -> str:
    body = "\n".join(f"{k} = {v:.6f}" if isinstance(v, float) else f"{k} = {v}" for k, v in kv.items())
    return f"[{name}]\n{body}\n"


def placed(kind: str, x: float, y: float, colour: str, **kv) -> dict:
    return dict(type=kind, mode=0, xpos=float(px(x)), ypos=float(px(y)), scale=1.0, rotation=0.0,
                colour=colour, **kv)


def main() -> None:
    gears = {"GearR": "R", "GearN": "N", **{f"Gear{i}": str(i) for i in range(1, 8)}}
    textures = {
        "Panel": tex_panel(),
        "Led": tex_led(),
        **{k: tex_text(v, 84, 90, 96, bold=True) for k, v in gears.items()},
        "LabelWater": tex_text("WATER", 12, 74, 20, align="left"),
        "LabelRadWater": tex_text("RAD WATER", 12, 74, 20, align="left"),
        "LabelOil": tex_text("OIL", 12, 74, 20, align="left"),
        "UnitKmh": tex_text("km/h", 11, 34, 20, align="left"),
        "UnitRpm": tex_text("rpm", 11, 34, 20, align="left"),
        "UnitC": tex_text("°C", 11, 20, 20, align="left"),
    }
    sheets = {name: font_sheet(ttf, size) for name, (ttf, size) in FONTS.items()}
    build_atlas(textures, {name: (sheet, glyphs) for name, (sheet, glyphs, _) in sheets.items()})
    line_h = {name: h for name, (_, _, h) in sheets.items()}

    def number(key: str, data: str, font: str, size: float, right_x: float, box_y: float, box_h: float,
               **extra) -> str:
        """Right-aligned number, vertically centered in the SimHub text box (box_y, box_h at 1x)."""
        scale = size / FONTS[font][1]
        y = px(box_y + box_h / 2) - line_h[font] * scale / 2
        return section(key, type="Number", data=data, mode=0, xpos=float(px(right_x)), ypos=float(y),
                       scale=scale, rotation=0.0, colour=WHITE, font=font, format="Whole",
                       justification="Right", prefixenabled="false", suffixenabled="false", **extra)

    parts = [section("main", author=design.AUTHOR, atlas=f"textures\\{NAME}.ini",
                     description="ILLMNR RBR Engine",
                     autohidewhennodamage="false", autohidetime=5.0, type="simple")]
    # effects
    parts.append(section("upshift", type="Effect", effecttype="Blink|ColourChange|", data="UpShift",
                         blinkspeed=150.0, newcolour=RED))
    parts.append(section("coolanthot", type="Effect", effecttype="ColourChange|",
                         data="CoolantTemperatureWarning", newcolour=RED))
    parts.append(section("oilhot", type="Effect", effecttype="ColourChange|",
                         data="OilTemperatureWarning", newcolour=RED))

    parts.append(section("panel", **placed("Static", 0, 0, WHITE, texture="Panel")))

    # shift lights: each shows from its RPM percent upwards
    lw, gap = 22, 4
    row_w = len(SHIFT_LIGHTS) * (lw + gap) - gap
    lx = (PW - row_w) / 2
    for i, (threshold, colour) in enumerate(SHIFT_LIGHTS):
        parts.append(section(f"shift{i + 1}", **placed("Simple", lx + i * (lw + gap), 8, colour, texture="Led",
                                                       data="RPMPercent", effect="upshift",
                                                       rangemin=float(threshold), rangemax=1000.0)))

    # gear: RBR gear index 0=R, 1=N, 2=1st ...
    for idx, tex in enumerate(["GearR", "GearN"] + [f"Gear{i}" for i in range(1, 8)]):
        parts.append(section(f"gear_{tex.lower()}", **placed("Simple", PW / 2 - 45, 18, WHITE, texture=tex,
                                                            data="Gear", equal=idx)))

    # right block: speed + rpm (numbers right-aligned at the value box's right edge)
    rx = PW - SIDE - 36 - 84
    parts.append(number("speed", "SpeedKPH", NUM_BOLD, 34, rx + 84, 30, 40))
    parts.append(section("speed_unit", **placed("Static", rx + 86, 44, DIM, texture="UnitKmh")))
    parts.append(number("rpm", "RPM", NUM, 18, rx + 84, 70, 24))
    parts.append(section("rpm_unit", **placed("Static", rx + 86, 74, DIM, texture="UnitRpm")))

    # left block: temperatures
    temps = [("water", "LabelWater", "CoolantTemperatureC", "coolanthot"),
             ("radwater", "LabelRadWater", "RadiatorCoolantTemperatureC", None),
             ("oil", "LabelOil", "OilTemperatureC", "oilhot")]
    for i, (key, label, data, effect) in enumerate(temps):
        y = 34 + i * 22
        parts.append(section(f"{key}_label", **placed("Static", SIDE, y, DIM, texture=label)))
        extra = {"effect": effect} if effect else {}
        parts.append(number(key, data, NUM_BOLD, 15, SIDE + 112, y, 20, **extra))
        parts.append(section(f"{key}_unit", **placed("Static", SIDE + 114, y, DIM, texture="UnitC")))

    out = ROOT / "Custom"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{NAME}.element").write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out / f'{NAME}.element'} and textures/{NAME}.png/.ini")


if __name__ == "__main__":
    main()
