"""飞行计划模型。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class FlightPlanWaypoint(BaseModel):
    ident: str
    type: str                      # APT / NDB / VOR / FIX / UNKNOWN
    airway: str = "DRCT"           # DRCT 或航路名；机场点为 ADEP/ADES
    altitude_ft: float | None = None
    latitude: float | None = None
    longitude: float | None = None


class FlightPlan(BaseModel):
    departure: str                 # ICAO
    destination: str               # ICAO
    departure_runway: str | None = None
    arrival_runway: str | None = None
    sid: str | None = None
    star: str | None = None
    cycle: str | None = None       # AIRAC，如 "2503"
    waypoints: list[FlightPlanWaypoint] = Field(default_factory=list)
