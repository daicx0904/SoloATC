"""模拟飞机状态提供者：连接 Core 并周期发送 AircraftState。"""
from __future__ import annotations

import asyncio
import time
from uuid import uuid4

from services.ipc.client import IPCClient
from services.ipc.message import Message
from shared.enums import MessageType
from shared.schemas import AircraftState


class MockAircraftStateProvider:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 4200,
        callsign: str = "CES1234",
        interval: float = 0.5,
    ) -> None:
        self.client = IPCClient(host, port)
        self.callsign = callsign
        self.interval = interval
        self._lat = 40.072361
        self._lon = 116.597500
        self._alt = 0.0

    async def run(self, steps: int | None = None) -> None:
        await self.client.connect()
        await self._send_hello()
        i = 0
        while steps is None or i < steps:
            await self._send_state()
            i += 1
            await asyncio.sleep(self.interval)

    async def _send_hello(self) -> None:
        await self.client.send(Message(
            id=uuid4().hex,
            type=MessageType.HELLO,
            ts_mono=time.monotonic(),
            payload={"client_type": "mock-aircraft", "protocol_version": 1},
        ))

    async def _send_state(self) -> None:
        self._alt += 500.0
        state = AircraftState(
            callsign=self.callsign,
            latitude=self._lat,
            longitude=self._lon,
            altitude_msl_m=self._alt,
            indicated_altitude_m=self._alt,
            heading_deg=0.0,
            track_deg=0.0,
            groundspeed_kt=0.0,
            vertical_speed_mps=0.0,
            on_ground=self._alt <= 0.0,
            gear_down=True,
            flaps_ratio=0.0,
            timestamp=time.time(),
            groundspeed_valid=True,
        )
        await self.client.send(Message(
            id=uuid4().hex,
            type=MessageType.AIRCRAFT_STATE_UPDATED,
            ts_sim=time.time(),
            ts_mono=time.monotonic(),
            payload={"state": state.model_dump(), "source": "mock"},
        ))
