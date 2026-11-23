"""FlightSession 持久化（单文件 JSON）。"""
from __future__ import annotations

from pathlib import Path

from core.session.session import FlightSession


class FlightSessionStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, session: FlightSession) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(session.model_dump_json(indent=2), encoding="utf-8")

    def load(self) -> FlightSession | None:
        if not self.path.exists():
            return None
        return FlightSession.model_validate_json(self.path.read_text(encoding="utf-8"))
