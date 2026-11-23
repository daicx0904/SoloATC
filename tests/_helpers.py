"""测试共用工具。"""
import time

from shared.schemas import AircraftState


def valid_state(callsign: str = "CES1234", **over) -> AircraftState:
    base = {
        "callsign": callsign, "latitude": 40.0, "longitude": 116.0,
        "altitude_msl_ft": 1000.0, "indicated_altitude_ft": 1000.0,
        "heading_deg": 0.0, "track_deg": 0.0, "groundspeed_kt": 0.0,
        "vertical_speed_fpm": 0.0, "on_ground": True, "gear_down": True,
        "flaps_ratio": 0.0, "timestamp": time.time(), "groundspeed_valid": True,
    }
    base.update(over)
    return AircraftState(**base)
