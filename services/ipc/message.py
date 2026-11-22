"""IPC 消息模型与编解码。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared.enums import MessageType


class Message(BaseModel):
    id: str
    type: MessageType
    ts_sim: float | None = None
    ts_mono: float | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    def encode(self) -> bytes:
        return (self.model_dump_json() + "\n").encode("utf-8")
