"""Build the RBR stage time and delta overlays (same size, place them freely).

    python simhub/rbr/build_time.py   ->  dist/simhub/rbr/RBR_Time.simhubdash, RBR_Delta.simhubdash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for the illmnr package

from illmnr.design import DIM, GREEN, PAD, PANEL, RED, TRACK, WHITE
from illmnr.rbr import RAW, build
from illmnr.simhubdash import formula, gradient, hbar, layer, rect, text

# ---- tuning ----
SCALE = 1.2
DELTA_RANGE = 1.0      # seconds at which the delta text reaches full green / red
DELTA_BAR_RANGE = 10.0  # seconds at which the delta bar reaches the end

PW, PH = 184, 66  # panel size (1x)
W, H = PW + 2 * PAD, PH + 2 * PAD
DELTA = "[PersistantTrackerPlugin.AllTimeBestLiveDeltaSeconds]"  # SimHub: live delta to all-time best


def panel(name: str, label: str, value: list[dict]) -> dict:
    x0, y0 = PAD, PAD
    return layer(name, [
        rect(f"{name}.bg", x0, y0, PW, PH, PANEL, radius=8),
        text(f"{name}.label", x0 + 10, y0 + 4, 80, 14, label, size=10, color=DIM, bold=True, align="left"),
        *value,
    ], x0, y0, PW, PH)


def stage_time() -> dict:
    # tenths are truncated (not rounded) so 59.96 s never shows as "00:60.0"
    tenths = f"floor([{RAW}.stage.raceTime] * 10)"
    minutes = f"floor({tenths} / 600)"
    expr = f"format({minutes}, '00') + ':' + format(({tenths} - {minutes} * 600) / 10, '00.0')"
    return panel("time", "TIME", [
        text("time.value", PAD, PAD + 14, PW, 46, "00:00.0", size=32, bold=True,
             bindings=[formula("Text", expr)]),
    ])


def delta() -> dict:
    d = f"isnull({DELTA}, 0)"
    expr = f"if(isnull({DELTA}), '--.--', if({DELTA} > 0, '+', '') + format({DELTA}, '0.00'))"

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
    build("RBR_Time", "RBR Time", "Stage time for Richard Burns Rally (NGP UDP telemetry)",
          W, H, [stage_time()], sx=SCALE)
    build("RBR_Delta", "RBR Delta", "Live delta to best time for Richard Burns Rally",
          W, H, [delta()], sx=SCALE)
