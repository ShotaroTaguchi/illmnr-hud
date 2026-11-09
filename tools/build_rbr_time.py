"""Build the RBR stage time and delta overlays (same size, place them freely).

    python tools/build_rbr_time.py   ->  dist/RBR_Time.simhubdash, dist/RBR_Delta.simhubdash
"""
from rbr_common import DIM, GREEN, PAD, PANEL, RAW, RED, TRACK, WHITE, build
from simhubdash import formula, gradient, layer, rect, text

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

    # bar: faster (negative delta) -> green grows to the right, slower (positive) -> red grows to the left
    bx, by, bw, bh = PAD + 12, PAD + PH - 12, PW - 24, 5
    cx, half = bx + bw / 2, bw / 2
    # linear: DELTA_BAR_RANGE seconds = full half-bar (e.g. 1 s of 10 s -> 10%).
    # Width/Left bindings are not touched by scale(), so the expressions carry SCALE themselves
    green_w = f"min(1, max(0, -{d}) / {DELTA_BAR_RANGE}) * {half * SCALE}"
    red_w = f"min(1, max(0, {d}) / {DELTA_BAR_RANGE}) * {half * SCALE}"
    return panel("delta", "DELTA", [
        text("delta.value", PAD, PAD + 12, PW, 40, "--.--", size=32, bold=True,
             bindings=[formula("Text", expr),
                       gradient("TextColor", d, [(-DELTA_RANGE, GREEN), (0, WHITE), (DELTA_RANGE, RED)])]),
        rect("delta.bar.track", bx, by, bw, bh, TRACK, radius=2),
        rect("delta.bar.faster", cx, by, 0, bh, GREEN, radius=2,
             bindings=[formula("Width", green_w)]),
        rect("delta.bar.slower", cx, by, 0, bh, RED, radius=2,
             bindings=[formula("Width", red_w), formula("Left", f"{cx * SCALE} - {red_w}")]),
        rect("delta.bar.center", cx - 1, by - 3, 2, bh + 6, WHITE),
    ])


if __name__ == "__main__":
    build("RBR_Time", "RBR Time", "Stage time for Richard Burns Rally (NGP UDP telemetry)",
          W, H, [stage_time()], sx=SCALE)
    build("RBR_Delta", "RBR Delta", "Live delta to best time for Richard Burns Rally",
          W, H, [delta()], sx=SCALE)
