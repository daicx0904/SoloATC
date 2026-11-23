"""Core 入口：python -m core"""
import asyncio
import logging
from pathlib import Path

from core.service import CoreService

logger = logging.getLogger("core")


async def main() -> None:
    store = Path("data/events.jsonl")
    core = CoreService(event_store_path=store)
    logger.info("Core 启动，事件存储: %s", store.resolve())
    await core.run_forever()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    asyncio.run(main())
