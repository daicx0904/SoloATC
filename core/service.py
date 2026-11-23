"""Core 服务：事件总线 + 存储 + IPC Server（Headless 可运行）。"""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from core.events.bus import EventBus
from core.events.store import EventStore
from services.ipc.message import Message
from services.ipc.server import IPCServer
from shared.enums import MessageType
from shared.schemas import AircraftState, Event

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = 1


def _validation_reason(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
    )


class CoreService:
    def __init__(self, event_store_path: str | Path, host: str = "127.0.0.1", port: int = 4200) -> None:
        self.bus = EventBus()
        self.store = EventStore(event_store_path)
        self.server = IPCServer(host, port)
        self.server.set_message_handler(self._on_message)
        self._latest_state: AircraftState | None = None
        self._event_count = 0
        self._recover()

    def _recover(self) -> None:
        """从持久化事件恢复最新状态与事件计数（支持 Core 重启后快照）。"""
        for event in self.store.load():
            self._event_count += 1
            if event.event_type == MessageType.AIRCRAFT_STATE_UPDATED.value:
                try:
                    self._latest_state = AircraftState.model_validate(event.payload.get("state", {}))
                except ValidationError:
                    logger.warning("历史事件中的飞机状态无法解析，已跳过", exc_info=True)

    def state_summary(self) -> dict:
        return {
            "latest_state": self._latest_state.model_dump() if self._latest_state else None,
            "event_count": self._event_count,
        }

    async def _on_message(self, msg: Message, writer) -> None:
        if msg.type == MessageType.HELLO:
            await self.server.send(writer, Message(
                id=uuid4().hex,
                type=MessageType.WELCOME,
                ts_mono=time.monotonic(),
                payload={"protocol_version": PROTOCOL_VERSION, "state_summary": self.state_summary()},
            ))
        elif msg.type == MessageType.HEARTBEAT:
            await self.server.send(writer, Message(
                id=uuid4().hex,
                type=MessageType.HEARTBEAT,
                ts_mono=time.monotonic(),
                payload={},
            ))
        elif msg.type == MessageType.AIRCRAFT_STATE_UPDATED:
            try:
                state = AircraftState.model_validate(msg.payload.get("state", {}))
            except ValidationError as exc:
                logger.warning("收到无效飞机状态，已拒绝", exc_info=True)
                await self.server.send(writer, Message(
                    id=uuid4().hex,
                    type=MessageType.ERROR,
                    ts_mono=time.monotonic(),
                    payload={
                        "reply_to": msg.id,
                        "code": "invalid_aircraft_state",
                        "reason": _validation_reason(exc),
                    },
                ))
                return
            self._latest_state = state
            self._record(Event(
                event_type=MessageType.AIRCRAFT_STATE_UPDATED.value,
                ts_sim=msg.ts_sim,
                ts_mono=msg.ts_mono,
                source=msg.payload.get("source", "bridge"),
                payload={"state": state.model_dump()},
            ))
        # 其余消息类型在后续里程碑处理

    def _record(self, event: Event) -> None:
        self.store.append(event)
        self._event_count += 1
        self.bus.publish(event)

    async def start(self) -> None:
        await self.server.start()

    async def stop(self) -> None:
        await self.server.stop()

    async def run_forever(self) -> None:
        await self.start()
        try:
            await asyncio.Event().wait()
        finally:
            await self.stop()
