"""跨模块共享的数据模型（Pydantic v2）。"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AircraftState(BaseModel):
    """统一的标准化飞机状态。Core 只认此模型，不直接读 X-Plane DataRef。

    规范单位（已定，避免后续返工）：
    - 高度：米（m）；英尺（ft）作为派生显示字段后续再加
    - 水平速度：节（kt）
    - 垂直速度：米/秒（m/s）；fpm 派生字段后期加
    """

    callsign: str
    latitude: float
    longitude: float
    altitude_msl_m: float
    indicated_altitude_m: float
    heading_deg: float
    track_deg: float
    groundspeed_kt: float
    vertical_speed_mps: float  # 米/秒
    on_ground: bool
    gear_down: bool
    flaps_ratio: float
    timestamp: float
    groundspeed_valid: bool = True


class Clearance(BaseModel):
    """结构化管制许可。"""

    clearance_id: str
    controller: str
    callsign: str
    clearance_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    valid_from: float
    expires_at: float | None = None
    status: str
    source_rule: str | None = None


class RuleResult(BaseModel):
    """规则引擎统一结果。"""

    accepted: bool
    reason: str = ""
    violated_rules: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Event(BaseModel):
    """领域事件。"""

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    event_type: str
    flight_id: str | None = None
    ts_sim: float | None = None
    ts_mono: float | None = None
    source: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    clearance_id: str | None = None
    rule_version: str | None = None
