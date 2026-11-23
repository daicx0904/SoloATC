"""把 X-Plane 原始 DataRef 值转换为标准 AircraftState 字典。

纯标准库、无 Pydantic（Bridge 运行在 XPPython3 内嵌 Python，不能依赖第三方库）。
产出 dict 形状与 Core 的 shared.schemas.AircraftState 一致，由 Core 校验。

规范单位：高度=米(m)，水平速度=节(kt)，垂直速度=米/秒(m/s)。
"""
from __future__ import annotations

FT_TO_M = 0.3048
MS_TO_KT = 1.943844492
FPM_TO_MPS = 0.00508  # 英尺/分 -> 米/秒


def build_aircraft_state_dict(callsign: str, raw: dict, timestamp: float) -> dict:
    """raw 字段（X-Plane 原生单位）：
    latitude/longitude(度), elevation_m(米MSL), indicated_altitude_ft(英尺),
    heading_deg/track_deg(度), groundspeed_ms(米/秒), vertical_speed_fpm(英尺/分),
    on_ground(0/1), gear_down(0/1), flaps_ratio(0..1)
    """
    return {
        "callsign": callsign,
        "latitude": raw["latitude"],
        "longitude": raw["longitude"],
        "altitude_msl_m": raw["elevation_m"],
        "indicated_altitude_m": raw["indicated_altitude_ft"] * FT_TO_M,
        "heading_deg": raw["heading_deg"],
        "track_deg": raw["track_deg"],
        "groundspeed_kt": raw["groundspeed_ms"] * MS_TO_KT,
        "vertical_speed_mps": raw["vertical_speed_fpm"] * FPM_TO_MPS,
        "on_ground": bool(raw["on_ground"]),
        "gear_down": bool(raw["gear_down"]),
        "flaps_ratio": raw["flaps_ratio"],
        "timestamp": timestamp,
        "groundspeed_valid": raw["groundspeed_ms"] >= 0.0,
    }
