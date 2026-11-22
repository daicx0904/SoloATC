"""事件总线测试。"""
from core.events.bus import EventBus
from shared.schemas import Event


def test_dispatch_in_subscription_order():
    bus = EventBus()
    order: list[str] = []
    bus.subscribe("X", lambda e: order.append("first"))
    bus.subscribe("X", lambda e: order.append("second"))
    bus.subscribe("Y", lambda e: order.append("other"))
    bus.publish(Event(event_type="X"))
    assert order == ["first", "second"]


def test_unhandled_event_is_ignored():
    bus = EventBus()
    called: list[int] = []
    bus.subscribe("X", lambda e: called.append(1))
    bus.publish(Event(event_type="Z"))
    assert called == []
