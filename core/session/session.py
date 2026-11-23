"""飞行会话模型（spec §6.4 子集，随里程碑扩展）。"""
from __future__ import annotations

import time
from uuid import uuid4

from pydantic import BaseModel, Field

from shared.enums import FlightPhase


class FlightSession(BaseModel):
    """一次飞行的持久化会话。"""

    flight_id: str = Field(default_factory=lambda: uuid4().hex)
    callsign: str
    aircraft_type: str
    departure: str          # ICAO
    destination: str        # ICAO
    phase: FlightPhase = FlightPhase.PREFLIGHT
    flight_plan: dict | None = None   # 待 fms-parser 分支填充
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def touch(self) -> None:
        self.updated_at = time.time()
