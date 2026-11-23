"""FlightSession 模型与持久化测试。"""
from core.session.session import FlightSession
from core.session.store import FlightSessionStore
from shared.enums import FlightPhase


def _session(**over) -> FlightSession:
    base = {"callsign": "CES1234", "aircraft_type": "A320", "departure": "ZBAA", "destination": "ZSPD"}
    base.update(over)
    return FlightSession(**base)


def test_session_defaults():
    s = _session()
    assert s.phase == FlightPhase.PREFLIGHT
    assert s.flight_id != ""


def test_roundtrip():
    s = _session()
    r = FlightSession.model_validate_json(s.model_dump_json())
    assert r == s


def test_store_roundtrip(tmp_path):
    store = FlightSessionStore(tmp_path / "session.json")
    s = _session()
    store.save(s)
    loaded = store.load()
    assert loaded is not None
    assert loaded.flight_id == s.flight_id
    assert loaded.callsign == "CES1234"


def test_store_missing_returns_none(tmp_path):
    assert FlightSessionStore(tmp_path / "none.json").load() is None
