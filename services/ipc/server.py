"""IPC 服务端（asyncio TCP + JSON Lines）。"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from services.ipc.message import Message

logger = logging.getLogger(__name__)

MessageHandler = Callable[[Message, asyncio.StreamWriter], Awaitable[None]]


class IPCServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 4200) -> None:
        self.host = host
        self.port = port
        self._handler: MessageHandler | None = None
        self._server: asyncio.AbstractServer | None = None
        self._writers: set[asyncio.StreamWriter] = set()

    @property
    def bound_port(self) -> int | None:
        if self._server is None or not self._server.sockets:
            return None
        return self._server.sockets[0].getsockname()[1]

    def set_message_handler(self, handler: MessageHandler) -> None:
        self._handler = handler

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self._writers.add(writer)
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                    msg = Message.model_validate_json(line.decode("utf-8"))
                except ValueError:
                    logger.debug("丢弃无法解析的消息", exc_info=True)
                    continue
                if self._handler is not None:
                    await self._handler(msg, writer)
        finally:
            self._writers.discard(writer)
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                logger.debug("关闭连接时出错", exc_info=True)

    async def send(self, writer: asyncio.StreamWriter, msg: Message) -> None:
        writer.write(msg.encode())
        await writer.drain()

    async def broadcast(self, msg: Message) -> None:
        for w in list(self._writers):
            try:
                await self.send(w, msg)
            except OSError:
                logger.debug("广播到某客户端失败", exc_info=True)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
        for w in list(self._writers):
            w.close()
        self._writers.clear()
