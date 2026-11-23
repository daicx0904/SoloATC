"""边界错误处理测试。"""
import asyncio
import time

from core.service import CoreService
from services.ipc.client import IPCClient
from services.ipc.message import Message
from shared.enums import MessageType
from tests._helpers import valid_state


def test_invalid_state_gets_error_not_disconnect(tmp_path):
    async def scenario():
        core = CoreService(event_store_path=tmp_path / "events.jsonl", host="127.0.0.1", port=0)
        await core.start()
        client = IPCClient("127.0.0.1", core.server.bound_port)
        await client.connect()

        await client.send(Message(id="h1", type=MessageType.HELLO, payload={}))
        welcome = await client.receive()
        assert welcome.type == MessageType.WELCOME

        # 坏状态：缺 callsign
        await client.send(Message(
            id="bad1", type=MessageType.AIRCRAFT_STATE_UPDATED,
            ts_mono=time.monotonic(), payload={"state": {"latitude": 1.0}},
        ))
        err = await client.receive()
        assert err.type == MessageType.ERROR
        assert err.payload["code"] == "invalid_aircraft_state"
        assert err.payload["reply_to"] == "bad1"

        # 连接仍可用：再发一条正常状态，应被记录
        await client.send(Message(
            id="good1", type=MessageType.AIRCRAFT_STATE_UPDATED,
            ts_mono=time.monotonic(), payload={"state": valid_state().model_dump()},
        ))
        await asyncio.sleep(0.2)
        await client.close()
        await core.stop()

        states = [e for e in core.store.load() if e.event_type == MessageType.AIRCRAFT_STATE_UPDATED.value]
        assert len(states) == 1
        assert states[0].payload["state"]["callsign"] == "CES1234"

    asyncio.run(scenario())
