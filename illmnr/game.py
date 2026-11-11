"""A game for the SimHub target: where each value comes from (the per-game lookup table) and the build helper.

Panels (simhub/build_*.py) only ask for values by key, e.g. game.get("tyre_tread.FL"); each game module
(illmnr/rbr.py, illmnr/ac.py, ...) maps those keys to SimHub expressions already converted to the units below.
A key that a game does not map returns None, and the panel shows "--" / an empty bar instead.

Keys and units:
    gear, speed_kmh, rpm                   standard values
    rpm_pct, redline                       SimHub's displayed RPM % (per-car redline) and "redline reached"
    water_c, radwater_c, oil_c             engine temperatures (deg C)
    tyre_tread.<c>, tyre_carcass.<c>, tyre_air.<c>   tyre temperatures (deg C), <c> = FL / FR / RL / RR
    tyre_pressure.<c>                      tyre pressure, in Game.pressure_unit
    tyre_left.<c>                          remaining tread (%, 100 = new)
    brake_temp.<c>                         brake disc temperature (deg C)
    brake_left.<c>                         remaining brake disc (%, 100 = new)
    steer                                  steering input (-1 = full left .. 1 = full right)
    clutch, brake, throttle, handbrake     pedal inputs (%)
    time_s                                 stage / lap time (seconds)
    driven_m, left_m                       distance driven / left to the finish (m)
    delta_s                                live delta to the best time (seconds; null = no reference)
"""
from dataclasses import dataclass
from pathlib import Path

from illmnr.design import AUTHOR, PREFIX
from illmnr.simhubdash import dashboard, scale, write_simhubdash

GD = "DataCorePlugin.GameData.NewData"  # SimHub's standard (game-independent) values
CORNERS = ("FL", "FR", "RL", "RR")
DIST_ROOT = Path(__file__).resolve().parent.parent / "dist" / "simhub"


def prop(name: str) -> str:
    """Standard property -> expression."""
    return f"[{GD}.{name}]"


# Same in every game SimHub supports
STANDARD = {
    "gear": prop("Gear"),
    "speed_kmh": prop("SpeedKmh"),
    "rpm": prop("Rpms"),
    "rpm_pct": prop("CarSettings_CurrentDisplayedRPMPercent"),
    "redline": prop("CarSettings_RPMRedLineReached"),
    "delta_s": "[PersistantTrackerPlugin.AllTimeBestLiveDeltaSeconds]",
}


@dataclass
class Game:
    key: str          # short name used in file names and titles: ILLMNR_<key>_Engine, "ILLMNR <key> Engine"
    name: str         # full name for descriptions
    source: str       # where the data comes from, appended to descriptions (may be "")
    props: dict[str, str]
    pressure_unit: str = "kPa"

    def get(self, key: str) -> str | None:
        return self.props.get(key)

    def build(self, panel: str, description: str, width: int, height: int, items: list[dict],
              sx: float = 1.0, sy: float | None = None, with_source: bool = True) -> None:
        """Write dist/simhub/<key>/ILLMNR_<key>_<panel>.simhubdash (title "ILLMNR <key> <panel>").
        Layouts are written at 1x; sx/sy set the default size."""
        sy = sx if sy is None else sy
        scale(items, sx, sy)
        desc = f"{description} for {self.name}" + (f" ({self.source})" if with_source and self.source else "")
        dash, meta = dashboard(title=f"{PREFIX} {self.key} {panel}", description=desc, author=AUTHOR,
                               width=round(width * sx), height=round(height * sy), items=items)
        out = write_simhubdash(dash, meta, f"{PREFIX}_{self.key}_{panel}", DIST_ROOT / self.key.lower())
        print(f"wrote {out}")


def games() -> list[Game]:
    """Every game a SimHub overlay is built for."""
    from illmnr.ac import AC
    from illmnr.rbr import RBR
    return [RBR, AC]
