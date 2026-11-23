"""带自动重连的 IPC 客户端封装。"""
from __future__ import annotations

import asyncio
import logging
import time
from uuid import uuid4

from services.ipc.client import IPCClient
from services.ipc.message import Message
from shared.enums import MessageType

logger = logging.getLogger(__name__)


class ReconnectingClient:
    """在 IPCClient 之上提供：连接重试 + 断开后重连 + 重新握手拿 state_summary。"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 4200,
        retry_delay: float = 0.5,
        max_retries: int = 5,
    ) -> None:
        self._client = IPCClient(host, port)
        self.retry_delay = retry_delay
        self.max_retries = max_retries

    async def connect_with_retry(self) -> bool:
        """尝试连接，失败则指数退避重试；返回是否成功。"""
        for attempt in range(self.max_retries + 1):
            try:
                await self._client.connect()
                return True
            except OSError:
                if attempt >= self.max_retries:
                    logger.warning("连接 Core 失败，已达最大重试次数")
                    return False
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        return False

    async def hello(self) -> Message | None:
        """发 HELLO 并收 WELCOME（含 state_summary）。"""
        await self._client.send(Message(
            id=uuid4().hex,
            type=MessageType.HELLO,
            ts_mono=time.monotonic(),
            payload={"client_type": "reconnecting", "protocol_version": 1},
        ))
        return await self._client.receive()

    async def reconnect(self) -> Message | None:
        """断开后重连并重新握手，返回新的 WELCOME。"""
        await self._client.close()
        if not await self.connect_with_retry():
            return None
        return await self.hello()

    @property
    def client(self) -> IPCClient:
        return self._client
