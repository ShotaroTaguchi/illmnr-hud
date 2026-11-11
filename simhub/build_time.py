"""SimHub: stage time, delta and stage progress overlays (same size, place them freely), one set per game.

    python simhub/build_time.py   ->  dist/simhub/<game>/ILLMNR_<GAME>_Time / _Delta / _Stage.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root, for the illmnr package

from illmnr.design import DIM, GREEN, PAD, PANEL, RED, SMALL_H, SMALL_W, TRACK, WHITE
from illmnr.game import Game, games
from illmnr.simhubdash import formula, gradient, hbar, layer, rect, text

# ---- tuning ----
SCALE = 1.2
DELTA_RANGE = 1.0      # seconds at which the delta text reaches full green / red
DELTA_BAR_RANGE = 10.0  # seconds at which the delta bar reaches the end

PW, PH = SMALL_W, SMALL_H  # panel size (1x), shared with rbrhud/build_time.py
W, H = PW + 2 * PAD, PH + 2 * PAD


def panel(name: str, label: str, value: list[dict]) -> dict:
    x0, y0 = PAD, PAD
    return layer(name, [
        rect(f"{name}.bg", x0, y0, PW, PH, PANEL, radius=8),
        text(f"{name}.label", x0 + 10, y0 + 4, 80, 14, label, size=10, color=DIM, bold=True, align="left"),
        *value,
    ], x0, y0, PW, PH)


def stage_progress(g: Game) -> dict:
    """Distance left to the finish (big) and how much of the stage is done (bar + %)."""
    driven = g.get("driven_m")
    left = g.get("left_m")
    pct = f"if({driven} + {left} > 0, {driven} / ({driven} + {left}) * 100, 0)"
    bx, by, bw, bh = PAD + 12, PAD + PH - 12, PW - 24, 5
    return panel("stage", "STAGE", [
        text("stage.pct", PAD + PW - 60, PAD + 4, 50, 14, "0%", size=10, color=DIM, bold=True, align="right",
             bindings=[formula("Text", f"format({pct}, '0') + '%'")]),
        text("stage.left", PAD, PAD + 12, PW, 40, "0.0 km", size=30, bold=True,
             bindings=[formula("Text", f"format({left} / 1000, '0.0') + ' km'")]),
        hbar("stage.bar", bx, by, bw, bh, WHITE, back=TRACK, maximum=100, bindings=[formula("Value", pct)]),
    ])


def stage_time(g: Game) -> dict:
    # tenths are truncated (not rounded) so 59.96 s never shows as "00:60.0"
    tenths = f"floor({g.get('time_s')} * 10)"
    minutes = f"floor({tenths} / 600)"
    expr = f"format({minutes}, '00') + ':' + format(({tenths} - {minutes} * 600) / 10, '00.0')"
    return panel("time", "TIME", [
        text("time.value", PAD, PAD + 14, PW, 46, "00:00.0", size=32, bold=True,
             bindings=[formula("Text", expr)]),
    ])


def delta(g: Game) -> dict:
    delta_s = g.get("delta_s")
    d = f"isnull({delta_s}, 0)"
    expr = f"if(isnull({delta_s}), '--.--', if({delta_s} > 0, '+', '') + format({delta_s}, '0.00'))"

    # bar: faster (negative delta) -> green grows to the right, slower (positive) -> red grows to the left.
    # Two gauges meet at the center; linear, DELTA_BAR_RANGE seconds = full half (1 s of 10 s -> 10%).
    # Only if() is used (known to work); the gauges clamp at their Maximum.
    bx, by, bw, bh = PAD + 12, PAD + PH - 12, PW - 24, 5
    cx, half = bx + bw / 2, bw / 2
    faster = f"if({d} < 0, -{d}, 0)"
    slower = f"if({d} > 0, {d}, 0)"
    return panel("delta", "DELTA", [
        text("delta.value", PAD, PAD + 12, PW, 40, "--.--", size=32, bold=True,
             bindings=[formula("Text", expr),
                       gradient("TextColor", d, [(-DELTA_RANGE, GREEN), (0, WHITE), (DELTA_RANGE, RED)])]),
        hbar("delta.bar.slower", bx, by, half, bh, RED, back=TRACK, maximum=DELTA_BAR_RANGE,
             from_right=True, bindings=[formula("Value", slower)]),
        hbar("delta.bar.faster", cx, by, half, bh, GREEN, back=TRACK, maximum=DELTA_BAR_RANGE,
             bindings=[formula("Value", faster)]),
        rect("delta.bar.center", cx - 1, by - 3, 2, bh + 6, WHITE),
    ])


if __name__ == "__main__":
    for g in games():
        g.build("Time", "Stage time", W, H, [stage_time(g)], sx=SCALE)
        g.build("Delta", "Live delta to best time", W, H, [delta(g)], sx=SCALE, with_source=False)
        g.build("Stage", "Distance to finish and stage progress", W, H, [stage_progress(g)], sx=SCALE,
                with_source=False)
