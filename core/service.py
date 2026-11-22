"""Core 服务：事件总线 + 存储 + IPC Server（Headless 可运行）。"""
from __future__ import annotations

import asyncio
import time
from pathlib import Path
from uuid import uuid4

from core.events.bus import EventBus
from core.events.store import EventStore
from services.ipc.message import Message
from services.ipc.server import IPCServer
from shared.enums import MessageType
from shared.schemas import AircraftState, Event

PROTOCOL_VERSION = 1


class CoreService:
    def __init__(self, event_store_path: str | Path, host: str = "127.0.0.1", port: int = 4200) -> None:
        self.bus = EventBus()
        self.store = EventStore(event_store_path)
        self.server = IPCServer(host, port)
        self.server.set_message_handler(self._on_message)

    async def _on_message(self, msg: Message, writer) -> None:
        if msg.type == MessageType.HELLO:
            await self.server.send(writer, Message(
                id=uuid4().hex,
                type=MessageType.WELCOME,
                ts_mono=time.monotonic(),
                payload={"protocol_version": PROTOCOL_VERSION},
            ))
        elif msg.type == MessageType.HEARTBEAT:
            await self.server.send(writer, Message(
                id=uuid4().hex,
                type=MessageType.HEARTBEAT,
                ts_mono=time.monotonic(),
                payload={},
            ))
        elif msg.type == MessageType.AIRCRAFT_STATE_UPDATED:
            state = AircraftState.model_validate(msg.payload.get("state", {}))
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
