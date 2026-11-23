"""断线重连测试。"""
import asyncio
import time
from uuid import uuid4

from core.service import CoreService
from services.ipc.message import Message
from services.ipc.reconnecting import ReconnectingClient
from shared.enums import MessageType
from tests._helpers import valid_state


def test_reconnect_gets_state_summary(tmp_path):
    async def scenario():
        store_path = tmp_path / "events.jsonl"
        core = CoreService(event_store_path=store_path, host="127.0.0.1", port=0)
        await core.start()
        port = core.server.bound_port

        client = ReconnectingClient("127.0.0.1", port)
        assert await client.connect_with_retry() is True
        w1 = await client.hello()
        assert w1 is not None and w1.type == MessageType.WELCOME

        # 发一条状态并记录
        await client.client.send(Message(
            id=uuid4().hex, type=MessageType.AIRCRAFT_STATE_UPDATED,
            ts_mono=time.monotonic(),
            payload={"state": valid_state().model_dump(), "source": "test"},
        ))
        await asyncio.sleep(0.2)

        # 模拟 Core 重启（同一端口，reuse_address 保证可立即重绑）
        await core.stop()
        core2 = CoreService(event_store_path=store_path, host="127.0.0.1", port=port)
        await core2.start()

        # 重连并拿 state_summary
        w2 = await client.reconnect()
        assert w2 is not None and w2.type == MessageType.WELCOME
        assert w2.payload["state_summary"]["event_count"] == 1
        assert w2.payload["state_summary"]["latest_state"]["callsign"] == "CES1234"

        await core2.stop()
        await client.client.close()

    asyncio.run(scenario())
