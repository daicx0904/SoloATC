"""状态摘要测试（重连 / 重启）。"""
import asyncio
import time
from uuid import uuid4

from core.service import CoreService
from services.ipc.client import IPCClient
from services.ipc.message import Message
from shared.enums import MessageType
from tests._helpers import valid_state


def test_state_summary_on_reconnect(tmp_path):
    async def scenario():
        core = CoreService(event_store_path=tmp_path / "events.jsonl", host="127.0.0.1", port=0)
        await core.start()

        c1 = IPCClient("127.0.0.1", core.server.bound_port)
        await c1.connect()
        await c1.send(Message(id="h1", type=MessageType.HELLO, payload={}))
        w1 = await c1.receive()
        assert w1.payload["state_summary"]["latest_state"] is None
        assert w1.payload["state_summary"]["event_count"] == 0

        await c1.send(Message(id=uuid4().hex, type=MessageType.AIRCRAFT_STATE_UPDATED,
                              ts_mono=time.monotonic(), payload={"state": valid_state().model_dump()}))
        await asyncio.sleep(0.2)
        await c1.close()

        c2 = IPCClient("127.0.0.1", core.server.bound_port)
        await c2.connect()
        await c2.send(Message(id="h2", type=MessageType.HELLO, payload={}))
        w2 = await c2.receive()
        assert w2.payload["state_summary"]["latest_state"]["callsign"] == "CES1234"
        assert w2.payload["state_summary"]["event_count"] == 1
        await c2.close()
        await core.stop()

    asyncio.run(scenario())


def test_state_summary_survives_restart(tmp_path):
    async def scenario():
        store_path = tmp_path / "events.jsonl"

        core = CoreService(event_store_path=store_path, host="127.0.0.1", port=0)
        await core.start()
        c1 = IPCClient("127.0.0.1", core.server.bound_port)
        await c1.connect()
        await c1.send(Message(id="h1", type=MessageType.HELLO, payload={}))
        await c1.receive()
        await c1.send(Message(id=uuid4().hex, type=MessageType.AIRCRAFT_STATE_UPDATED,
                              ts_mono=time.monotonic(), payload={"state": valid_state().model_dump()}))
        await asyncio.sleep(0.2)
        await c1.close()
        await core.stop()

        core2 = CoreService(event_store_path=store_path, host="127.0.0.1", port=0)
        await core2.start()
        c2 = IPCClient("127.0.0.1", core2.server.bound_port)
        await c2.connect()
        await c2.send(Message(id="h2", type=MessageType.HELLO, payload={}))
        w2 = await c2.receive()
        assert w2.payload["state_summary"]["latest_state"]["callsign"] == "CES1234"
        assert w2.payload["state_summary"]["event_count"] == 1
        await c2.close()
        await core2.stop()

    asyncio.run(scenario())
