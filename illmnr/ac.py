"""Assetto Corsa (the original) for the SimHub target: SimHub's standard values only (DataCorePlugin.GameData.NewData).

Values SimHub does not give in the standard set are left out for now (the panels show "--" / an empty bar):
carcass and air temperature of the tyres, brake disc wear, radiator water, steering.
NOT CHECKED ON A REAL PC YET: every name below is from SimHub's property list as remembered, check them in
SimHub (Available properties) while driving. In particular: whether AC fills WaterTemperature / OilTemperature,
the tyre pressure unit (psi assumed), whether TyreWear* is wear or remaining, and Handbrake.
"""
from illmnr.game import CORNERS, STANDARD, Game, prop

# SimHub's corner names
SIDE = {"FL": "FrontLeft", "FR": "FrontRight", "RL": "RearLeft", "RR": "RearRight"}


def _props() -> dict[str, str]:
    p = dict(STANDARD)
    p["water_c"] = prop("WaterTemperature")
    p["oil_c"] = prop("OilTemperature")

    for c in CORNERS:
        s = SIDE[c]
        p[f"tyre_tread.{c}"] = prop(f"TyreTemperature{s}")
        p[f"tyre_pressure.{c}"] = prop(f"TyrePressure{s}")
        p[f"tyre_left.{c}"] = f"100 - {prop(f'TyreWear{s}')}"  # assumed: wear % (0 = new)
        p[f"brake_temp.{c}"] = prop(f"BrakeTemperature{s}")

    for pedal, name in (("clutch", "Clutch"), ("brake", "Brake"), ("throttle", "Throttle"), ("handbrake", "Handbrake")):
        p[pedal] = prop(name)  # already 0..100

    # circuits: the "stage" is the current lap
    p["time_s"] = f"timespantoseconds({prop('CurrentLapTime')})"
    pos = prop("TrackPositionPercent")  # 0..1 around the lap
    length = prop("TrackLength")  # m
    p["driven_m"] = f"{pos} * {length}"
    p["left_m"] = f"(1 - {pos}) * {length}"
    return p


AC = Game(key="AC", name="Assetto Corsa", source="", props=_props(), pressure_unit="psi")
