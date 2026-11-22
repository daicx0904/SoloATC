"""事件存储测试。"""
from core.events.store import EventStore
from shared.schemas import Event


def test_roundtrip(tmp_path):
    store = EventStore(tmp_path / "events.jsonl")
    store.append(Event(event_type="A", source="test"))
    store.append(Event(event_type="B", source="test"))
    loaded = store.load()
    assert len(loaded) == 2
    assert [e.event_type for e in loaded] == ["A", "B"]


def test_empty_when_missing(tmp_path):
    store = EventStore(tmp_path / "none.jsonl")
    assert store.load() == []
