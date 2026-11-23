"""X-Plane / SimBrief .fms 解析器。

支持两种格式（已用真实 .fms 文件核对）：
- 新格式（XP11/XP12）：首行 I，含 "1100 Version"、CYCLE、ADEP/ADES、DEPRWY/DESRWY、SID/STAR、NUMENR，
  航路点行 "<type> <ident> <airway> <alt_ft> <lat> <lon>"。
- 旧格式（XP9/10）：dep / arr / flight_number，之后航路点与航路交替，以 "99" 结束。
"""
from __future__ import annotations

from core.navigation.flight_plan import FlightPlan, FlightPlanWaypoint

WP_TYPE_MAP = {"1": "APT", "2": "NDB", "3": "VOR", "11": "FIX"}

_END_MARKERS = {"99", "0", "1"}


class FmsParseError(ValueError):
    """.fms 解析失败。"""


def parse_fms(text: str) -> FlightPlan:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise FmsParseError("空的 .fms 文件")
    if _is_new_format(lines):
        return _parse_new(lines)
    return _parse_old(lines)


def _is_new_format(lines: list[str]) -> bool:
    return any("Version" in ln or ln.startswith("1100") for ln in lines[:5])


def _parse_new(lines: list[str]) -> FlightPlan:
    dep = arr = ""
    dep_rwy = arr_rwy = sid = star = cycle = None
    waypoints: list[FlightPlanWaypoint] = []
    for ln in lines:
        if ln.startswith("ADEP "):
            dep = ln.split()[1]
        elif ln.startswith("ADES "):
            arr = ln.split()[1]
        elif ln.startswith("DEPRWY "):
            dep_rwy = ln.split()[1]
        elif ln.startswith("DESRWY "):
            arr_rwy = ln.split()[1]
        elif ln.startswith("SID "):
            sid = ln.split()[1]
        elif ln.startswith("STAR "):
            star = ln.split()[1]
        elif ln.startswith("CYCLE "):
            cycle = ln.split()[1]
        elif _is_new_waypoint_line(ln):
            wp = _parse_new_waypoint(ln)
            if wp is not None:
                waypoints.append(wp)
    if not dep or not arr:
        raise FmsParseError("新格式缺少 ADEP/ADES")
    return FlightPlan(
        departure=dep, destination=arr,
        departure_runway=dep_rwy, arrival_runway=arr_rwy,
        sid=sid, star=star, cycle=cycle, waypoints=waypoints,
    )


def _is_new_waypoint_line(ln: str) -> bool:
    parts = ln.split()
    return len(parts) >= 6 and parts[0].isdigit()


def _parse_new_waypoint(ln: str) -> FlightPlanWaypoint | None:
    parts = ln.split()
    code, ident, airway = parts[0], parts[1], parts[2]
    try:
        alt = float(parts[3])
        lat = float(parts[4])
        lon = float(parts[5])
    except ValueError:
        return None
    return FlightPlanWaypoint(
        ident=ident,
        type=WP_TYPE_MAP.get(code, "UNKNOWN"),
        airway=airway,
        altitude_ft=alt,
        latitude=lat,
        longitude=lon,
    )


def _parse_old(lines: list[str]) -> FlightPlan:
    if len(lines) < 3:
        raise FmsParseError("旧格式 .fms 至少需要 dep/arr/flight number")
    dep, arr = lines[0], lines[1]
    waypoints: list[FlightPlanWaypoint] = []
    i = 3  # 跳过 dep / arr / flight_number
    while i < len(lines):
        token = lines[i]
        if token.isdigit():  # 结束标记（99 等）
            break
        ident = token
        airway = "DRCT"
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt is not None and not nxt.isdigit():
            airway = nxt
            i += 2
        else:
            i += 1
        waypoints.append(FlightPlanWaypoint(ident=ident, type="FIX", airway=airway))
    return FlightPlan(departure=dep, destination=arr, waypoints=waypoints)
