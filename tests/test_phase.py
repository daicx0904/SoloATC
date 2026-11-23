"""飞行阶段状态机测试。"""
import pytest

from core.session.phase import FlightPhaseMachine, PhaseTransitionError
from shared.enums import FlightPhase


def test_valid_transition():
    m = FlightPhaseMachine(FlightPhase.PREFLIGHT)
    t = m.transition(FlightPhase.CLEARANCE, "IFR clearance issued")
    assert m.phase == FlightPhase.CLEARANCE
    assert t.from_phase == FlightPhase.PREFLIGHT
    assert t.to_phase == FlightPhase.CLEARANCE


def test_invalid_transition_raises():
    m = FlightPhaseMachine(FlightPhase.PREFLIGHT)
    with pytest.raises(PhaseTransitionError):
        m.transition(FlightPhase.TAXI, "bad trigger")


def test_history_records_each_transition():
    m = FlightPhaseMachine(FlightPhase.TAKEOFF)
    m.transition(FlightPhase.DEPARTURE, "airborne")
    assert len(m.history) == 1
    assert m.history[0].trigger == "airborne"


def test_can_transition():
    m = FlightPhaseMachine(FlightPhase.APPROACH)
    assert m.can_transition(FlightPhase.LANDING) is True
    assert m.can_transition(FlightPhase.GO_AROUND) is True
    assert m.can_transition(FlightPhase.TAKEOFF) is False
