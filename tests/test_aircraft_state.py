"""AircraftState 模型测试。"""
import pytest
from pydantic import ValidationError

from shared.schemas import AircraftState


def _state(**over) -> dict:
    base = {
        "callsign": "CES1234", "latitude": 40.07, "longitude": 116.6,
        "altitude_msl_m": 10668.0, "indicated_altitude_m": 10668.0,
        "heading_deg": 90.0, "track_deg": 92.0, "groundspeed_kt": 450.0,
        "vertical_speed_fpm": 0.0, "on_ground": False, "gear_down": False,
        "flaps_ratio": 0.0, "timestamp": 123.4, "groundspeed_valid": True,
    }
    base.update(over)
    return base


def test_roundtrip():
    s = AircraftState(**_state())
    restored = AircraftState.model_validate_json(s.model_dump_json())
    assert restored == s
    assert restored.callsign == "CES1234"


def test_requires_callsign():
    with pytest.raises(ValidationError):
        AircraftState(**_state(callsign=None))


def test_default_groundspeed_valid():
    s = AircraftState(**_state())
    s2 = AircraftState.model_validate(s.model_dump(exclude={"groundspeed_valid"}))
    assert s2.groundspeed_valid is True
