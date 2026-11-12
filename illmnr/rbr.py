"""Richard Burns Rally for the SimHub target: values from the NGP UDP telemetry (GameRawData.NGPTelemetry).

NGP temperatures are Kelvin and pressures Pa; they are converted here so panels get deg C / kPa.
NGP sends nothing during replays (RBRHUD covers replays).
"""
from illmnr.game import STANDARD, Game

RAW = "GameRawData.NGPTelemetry"  # NGP packet as exposed by SimHub
K = 273.15  # NGP temperatures are Kelvin

# NGP's suspension names for each corner
SUSP = {"FL": "suspensionLF", "FR": "suspensionRF", "RL": "suspensionLB", "RR": "suspensionRB"}


def c_of(expr_kelvin: str) -> str:
    """Kelvin expression -> Celsius expression."""
    return f"({expr_kelvin}) - {K}"


def _props() -> dict[str, str]:
    p = dict(STANDARD)
    engine = f"{RAW}.car.engine"
    p["water_c"] = c_of(f"[{engine}.engineCoolantTemperature]")
    p["radwater_c"] = c_of(f"[{engine}.radiatorCoolantTemperature]")
    # engineTemperature matches the in-car "Oil T" gauge, so it is shown as OIL
    p["oil_c"] = c_of(f"[{engine}.engineTemperature]")

    for c, susp in SUSP.items():
        tire = f"[{RAW}.car.{susp}.wheel.tire"
        p[f"tyre_tread.{c}"] = c_of(f"{tire}.treadTemperature]")
        p[f"tyre_carcass.{c}"] = c_of(f"{tire}.carcassTemperature]")
        p[f"tyre_air.{c}"] = c_of(f"{tire}.temperature]")
        p[f"tyre_pressure.{c}"] = f"{tire}.pressure] / 1000"
        p[f"tyre_left.{c}"] = f"100 - 100 * ({' + '.join(f'{tire}.segment{i}.wear]' for i in range(1, 9))}) / 8"
        disc = f"[{RAW}.car.{susp}.wheel.brakeDisk"
        p[f"brake_temp.{c}"] = c_of(f"{disc}.temperature]")
        p[f"brake_left.{c}"] = f"100 - 100 * {disc}.wear]"  # wear assumed 0 = new .. 1 = worn out (not verified)

    p["steer"] = f"[{RAW}.control.steering]"
    for pedal in ("clutch", "brake", "throttle", "handbrake"):
        p[pedal] = f"[{RAW}.control.{pedal}] * 100"

    p["time_s"] = f"[{RAW}.stage.raceTime]"
    p["driven_m"] = f"[{RAW}.stage.progress]"
    p["left_m"] = f"[{RAW}.stage.distanceToEnd]"
    return p


RBR = Game(key="RBR", name="Richard Burns Rally", source="NGP UDP telemetry", props=_props(), pressure_unit="kPa")
