"""X-Plane collector 单元测试。"""
import pytest

from adapters.xplane.collector import M_TO_FT, MS_TO_KT, build_aircraft_state_dict
from shared.schemas import AircraftState


def _raw(**over) -> dict:
    base = {
        "latitude": 40.07, "longitude": 116.6,
        "elevation_m": 1000.0,
        "indicated_altitude_ft": 3300.0,
        "heading_deg": 90.0, "track_deg": 92.0,
        "groundspeed_ms": 100.0,
        "vertical_speed_fpm": -500.0,
        "on_ground": 0, "gear_down": 1, "flaps_ratio": 0.0,
    }
    base.update(over)
    return base


def test_unit_conversion():
    d = build_aircraft_state_dict("CES1234", _raw(), 123.4)
    assert d["altitude_msl_ft"] == pytest.approx(1000.0 * M_TO_FT)
    assert d["groundspeed_kt"] == pytest.approx(100.0 * MS_TO_KT)
    assert d["on_ground"] is False
    assert d["gear_down"] is True
    assert d["groundspeed_valid"] is True


def test_groundspeed_invalid_when_negative():
    d = build_aircraft_state_dict("CES1234", _raw(groundspeed_ms=-1.0), 123.4)
    assert d["groundspeed_valid"] is False


def test_output_validates_as_aircraft_state():
    d = build_aircraft_state_dict("CES1234", _raw(), 123.4)
    AircraftState.model_validate(d)  # 不抛错即通过
