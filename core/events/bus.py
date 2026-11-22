"""确定性事件总线。"""
from __future__ import annotations

from collections.abc import Callable

from shared.schemas import Event

Handler = Callable[[Event], None]


class EventBus:
    """按事件类型分发；同一类型内按订阅顺序同步调用（确定性）。"""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers.get(event.event_type, ()):
            handler(event)

    def publish_all(self, events: list[Event]) -> None:
        for event in events:
            self.publish(event)
