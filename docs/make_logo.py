"""Render docs/images/logo.png (README header) from the ILLMNR-HUD palette.

    .venv/Scripts/python docs/make_logo.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from illmnr import design  # noqa: E402

SS = 2  # supersampling for smooth edges
W, H = 1280, 360
FONT_WORD = "C:/Windows/Fonts/bahnschrift.ttf"  # variable font; bold set below
FONT_SUB = "C:/Windows/Fonts/segoeui.ttf"


def rgba(color: str) -> tuple[int, int, int, int]:
    c = color.lstrip("#")
    return int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16), int(c[0:2], 16)


def main() -> None:
    w, h = W * SS, H * SS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=28 * SS, fill=rgba(design.PANEL))

    # shift lights row (the signature of the design)
    lw, lh, gap = 64 * SS, 16 * SS, 12 * SS
    n = len(design.SHIFT_LIGHTS)
    x0 = (w - (n * lw + (n - 1) * gap)) // 2
    y0 = 52 * SS
    for i, (_, color) in enumerate(design.SHIFT_LIGHTS):
        x = x0 + i * (lw + gap)
        d.rounded_rectangle([x, y0, x + lw, y0 + lh], radius=4 * SS, fill=rgba(color))

    # wordmark: ILLMNR (white) + -HUD (dim)
    word = ImageFont.truetype(FONT_WORD, 150 * SS)
    try:
        word.set_variation_by_name("Bold")
    except Exception:
        pass
    a, b = "ILLMNR", "-HUD"
    wa, wb = d.textlength(a, font=word), d.textlength(b, font=word)
    x = (w - (wa + wb)) / 2
    base = 228 * SS
    d.text((x, base), a, font=word, fill=rgba(design.WHITE), anchor="ls")
    d.text((x + wa, base), b, font=word, fill=rgba(design.DIM), anchor="ls")

    sub = ImageFont.truetype(FONT_SUB, 30 * SS)
    d.text((w / 2, 300 * SS), "illuminer  ·  heads-up display for sim racing", font=sub,
           fill=rgba(design.DIM), anchor="mm")

    out = ROOT / "docs" / "images" / "logo.png"
    im.resize((W, H), Image.LANCZOS).save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
