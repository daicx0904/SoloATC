"""Core 入口：python -m core"""
import asyncio
from pathlib import Path

from core.service import CoreService


async def main() -> None:
    store = Path("data/events.jsonl")
    core = CoreService(event_store_path=store)
    print(f"Core 启动，事件存储: {store.resolve()}")
    await core.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
