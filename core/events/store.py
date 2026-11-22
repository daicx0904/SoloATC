"""事件持久化（JSON Lines，按时间顺序追加）。"""
from __future__ import annotations

from pathlib import Path

from shared.schemas import Event


class EventStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: Event) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")

    def load(self) -> list[Event]:
        if not self.path.exists():
            return []
        events: list[Event] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(Event.model_validate_json(line))
        return events
