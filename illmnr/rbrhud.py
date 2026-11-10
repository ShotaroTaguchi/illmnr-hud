"""RBRHUD target: texture atlas (with embedded bitmap fonts) + .element writer.

RBRHUD facts this relies on (see docs/development.md):
- atlas PNG must be power-of-two in both directions
- fonts live inside the atlas ([FontName] charset=... + per-glyph rects); one element = one atlas,
  so the element's own atlas must contain the fonts it uses
- colours are 'aarrggbb'; white textures are tinted by an element's `colour`
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from illmnr import design
from illmnr.design import hud

DIST = Path(__file__).resolve().parents[1] / "dist" / "rbrhud" / "OverlayElements"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_CHARS = " 0123456789-.:%+"
WHITE_PX = (255, 255, 255, 255)


def section(name: str, **kv) -> str:
    body = "\n".join(f"{k} = {v:.6f}" if isinstance(v, float) else f"{k} = {v}" for k, v in kv.items())
    return f"[{name}]\n{body}\n"


def pow2(n: int) -> int:
    p = 1
    while p < n:
        p *= 2
    return p


class Element:
    """Collects textures + sections for one element, written in the 1x layout and scaled by `s`."""

    def __init__(self, name: str, s: float, fonts: dict[str, tuple[str, float]]):
        self.name = f"{design.PREFIX}_{name}"
        self.s = s
        self.fonts = {f"{design.PREFIX}_{k}": v for k, v in fonts.items()}  # short name -> (ttf, size at 1x)
        self.textures: dict[str, Image.Image] = {}
        self.parts: list[str] = []
        self.line_h: dict[str, int] = {}

    def px(self, v: float) -> int:
        return round(v * self.s)

    def font(self, short: str) -> str:
        return f"{design.PREFIX}_{short}"

    # ---- textures (drawn white unless noted; tinted by `colour`) ----
    def tex_rect(self, key: str, w: float, h: float, radius: float = 0, fill=WHITE_PX) -> str:
        im = Image.new("RGBA", (self.px(w), self.px(h)), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle([0, 0, self.px(w) - 1, self.px(h) - 1], radius=self.px(radius), fill=fill)
        self.textures[key] = im
        return key

    def tex_text(self, key: str, s: str, size: float, w: float, h: float, bold: bool = False,
                 align: str = "center") -> str:
        """White text in a fixed-size cell (every glyph of e.g. the gear sits at the same spot)."""
        font = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, self.px(size))
        im = Image.new("RGBA", (self.px(w), self.px(h)), (0, 0, 0, 0))
        anchor = {"left": "lm", "center": "mm", "right": "rm"}[align]
        x = {"left": 0, "center": self.px(w) / 2, "right": self.px(w)}[align]
        ImageDraw.Draw(im).text((x, self.px(h) / 2), s, font=font, fill=WHITE_PX, anchor=anchor)
        self.textures[key] = im
        return key

    def tex_image(self, key: str, im: Image.Image) -> str:
        self.textures[key] = im
        return key

    # ---- sections ----
    def add(self, name: str, **kv) -> None:
        self.parts.append(section(name, **kv))

    def placed(self, name: str, kind: str, x: float, y: float, colour: str, **kv) -> None:
        self.add(name, type=kind, mode=0, xpos=float(self.px(x)), ypos=float(self.px(y)), scale=1.0, rotation=0.0,
                 colour=hud(colour), **kv)

    def number(self, name: str, data: str, font: str, size: float, x: float, box_y: float, box_h: float,
               colour: str = design.WHITE, fmt: str = "Whole", justification: str = "Right", **kv) -> None:
        """Number vertically centered in the box (box_y, box_h at 1x). x is the anchor for `justification`."""
        full = self.font(font)
        scale = size / self.fonts[full][1]
        y = self.px(box_y + box_h / 2) - self._line_h(full) * scale / 2
        self.add(name, type="Number", data=data, mode=0, xpos=float(self.px(x)), ypos=float(y), scale=scale,
                 rotation=0.0, colour=hud(colour), font=full, format=fmt, justification=justification,
                 prefixenabled="false", suffixenabled="false", **kv)

    def _line_h(self, full: str) -> int:
        if full not in self.line_h:
            ttf, size = self.fonts[full]
            ascent, descent = ImageFont.truetype(ttf, self.px(size)).getmetrics()
            self.line_h[full] = ascent + descent
        return self.line_h[full]

    # ---- output ----
    def _font_sheet(self, ttf: str, size: float):
        font = ImageFont.truetype(ttf, self.px(size))
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
            d.text((gx, gy + ascent), ch, font=font, fill=WHITE_PX, anchor="ls")
        return sheet, glyphs

    def write(self, description: str) -> None:
        fonts = {n: self._font_sheet(ttf, size) for n, (ttf, size) in self.fonts.items()}
        items = {**self.textures, **{f"__font__{n}": sheet for n, (sheet, _) in fonts.items()}}
        width, pad = 1024, 4
        x = y = shelf = 0
        rects = {}
        for key, im in sorted(items.items(), key=lambda kv: -kv[1].height):  # shelf packer
            if x + im.width + pad > width:
                x, y, shelf = 0, y + shelf + pad, 0
            rects[key] = (x, y, im.width, im.height)
            x += im.width + pad
            shelf = max(shelf, im.height)
        atlas = Image.new("RGBA", (width, pow2(y + shelf)), (0, 0, 0, 0))
        for key, (ax, ay, _, _) in rects.items():
            atlas.paste(items[key], (ax, ay))
        tex_dir, el_dir = DIST / "textures", DIST / "Custom"
        tex_dir.mkdir(parents=True, exist_ok=True)
        el_dir.mkdir(parents=True, exist_ok=True)
        atlas.save(tex_dir / f"{self.name}.png")
        lines = ["[MAIN]", f"texture=textures/{self.name}.png", "[Objects]"]
        lines += [f"{n}={x},{y},{w},{h}" for n, (x, y, w, h) in rects.items() if not n.startswith("__font__")]
        for fname, (_, glyphs) in fonts.items():
            cx, cy, cw, ch = rects[f"__font__{fname}"]
            lines += ["", f"[{fname}]", f"charset={cx},{cy},{cw},{ch}"]
            lines += [f"{code}={gx},{gy},{gw},{gh}" for code, (gx, gy, gw, gh) in glyphs.items()]
        (tex_dir / f"{self.name}.ini").write_text("\n".join(lines) + "\n", encoding="utf-8")

        head = section("main", author=design.AUTHOR, atlas=f"textures\\{self.name}.ini", description=description,
                       autohidewhennodamage="false", autohidetime=5.0, type="simple")
        (el_dir / f"{self.name}.element").write_text("\n".join([head] + self.parts), encoding="utf-8")
        print(f"wrote {el_dir / f'{self.name}.element'} and textures/{self.name}.png/.ini")
