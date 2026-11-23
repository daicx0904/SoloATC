"""飞行阶段状态机（确定性，spec §10）。"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from shared.enums import FlightPhase

# 合法阶段跳转（有向图）
TRANSITIONS: dict[FlightPhase, frozenset[FlightPhase]] = {
    FlightPhase.PREFLIGHT: frozenset({FlightPhase.CLEARANCE}),
    FlightPhase.CLEARANCE: frozenset({FlightPhase.PUSHBACK}),
    FlightPhase.PUSHBACK: frozenset({FlightPhase.TAXI}),
    FlightPhase.TAXI: frozenset({FlightPhase.HOLD_SHORT, FlightPhase.TAXI_IN, FlightPhase.PARKED}),
    FlightPhase.HOLD_SHORT: frozenset({FlightPhase.LINE_UP}),
    FlightPhase.LINE_UP: frozenset({FlightPhase.TAKEOFF, FlightPhase.TAXI}),
    FlightPhase.TAKEOFF: frozenset({FlightPhase.DEPARTURE}),
    FlightPhase.DEPARTURE: frozenset({FlightPhase.CLIMB}),
    FlightPhase.CLIMB: frozenset({FlightPhase.CRUISE}),
    FlightPhase.CRUISE: frozenset({FlightPhase.DESCENT, FlightPhase.DIVERSION}),
    FlightPhase.DESCENT: frozenset({FlightPhase.ARRIVAL}),
    FlightPhase.ARRIVAL: frozenset({FlightPhase.APPROACH}),
    FlightPhase.APPROACH: frozenset({FlightPhase.LANDING, FlightPhase.GO_AROUND, FlightPhase.DIVERSION}),
    FlightPhase.LANDING: frozenset({FlightPhase.ROLLOUT, FlightPhase.GO_AROUND}),
    FlightPhase.ROLLOUT: frozenset({FlightPhase.TAXI_IN}),
    FlightPhase.TAXI_IN: frozenset({FlightPhase.PARKED}),
    FlightPhase.PARKED: frozenset(),
    FlightPhase.GO_AROUND: frozenset({FlightPhase.APPROACH, FlightPhase.DIVERSION}),
    FlightPhase.DIVERSION: frozenset({FlightPhase.CRUISE, FlightPhase.DESCENT, FlightPhase.ARRIVAL}),
}


class PhaseTransitionError(Exception):
    """非法阶段跳转。"""


@dataclass
class PhaseTransition:
    """一次阶段跳转记录。"""

    from_phase: FlightPhase
    to_phase: FlightPhase
    trigger: str
    timestamp: float = field(default_factory=time.time)


class FlightPhaseMachine:
    """确定性飞行阶段状态机：校验跳转、记录历史。"""

    def __init__(self, initial: FlightPhase = FlightPhase.PREFLIGHT) -> None:
        self.phase = initial
        self.history: list[PhaseTransition] = []

    def can_transition(self, to: FlightPhase) -> bool:
        return to in TRANSITIONS.get(self.phase, frozenset())

    def transition(self, to: FlightPhase, trigger: str) -> PhaseTransition:
        if not self.can_transition(to):
            raise PhaseTransitionError(f"非法阶段跳转: {self.phase.value} -> {to.value}")
        t = PhaseTransition(from_phase=self.phase, to_phase=to, trigger=trigger)
        self.phase = to
        self.history.append(t)
        return t
