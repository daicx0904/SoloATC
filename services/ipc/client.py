"""IPC 客户端（asyncio TCP）。"""
from __future__ import annotations

import asyncio
import logging

from services.ipc.message import Message

logger = logging.getLogger(__name__)


class IPCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 4200) -> None:
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)

    async def send(self, msg: Message) -> None:
        if self._writer is None:
            raise RuntimeError("IPCClient 未连接")
        self._writer.write(msg.encode())
        await self._writer.drain()

    async def receive(self) -> Message | None:
        if self._reader is None:
            raise RuntimeError("IPCClient 未连接")
        line = await self._reader.readline()
        if not line:
            return None
        return Message.model_validate_json(line.decode("utf-8"))

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                logger.debug("关闭连接时出错", exc_info=True)
            self._writer = None
            self._reader = None
