"""SoloATC 可用原型演示：Core + Mock 桥接 + 断线重连。

运行：uv run python scripts/demo.py
"""
import asyncio

from adapters.mock.provider import MockAircraftStateProvider
from core.service import CoreService
from services.ipc.reconnecting import ReconnectingClient


async def main() -> None:
    store = "data/demo-events.jsonl"
    core = CoreService(event_store_path=store, host="127.0.0.1", port=4200)
    await core.start()
    print("[demo] Core 启动，端口 4200")

    provider = MockAircraftStateProvider(host="127.0.0.1", port=4200, interval=0.3)
    provider_task = asyncio.create_task(provider.run(steps=5))

    client = ReconnectingClient("127.0.0.1", 4200)
    print("[demo] 客户端连接:", await client.connect_with_retry())
    welcome = await client.hello()
    print("[demo] WELCOME state_summary:", welcome.payload.get("state_summary"))

    await provider_task
    await asyncio.sleep(0.5)
    await core.stop()
    print("[demo] Core 已停止")

    core2 = CoreService(event_store_path=store, host="127.0.0.1", port=4200)
    await core2.start()
    print("[demo] Core 已重启")

    welcome2 = await client.reconnect()
    print("[demo] 重连后 state_summary:", welcome2.payload.get("state_summary") if welcome2 else None)

    await core2.stop()
    await client.client.close()
    print("[demo] 结束")


if __name__ == "__main__":
    asyncio.run(main())
