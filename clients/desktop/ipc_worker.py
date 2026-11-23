"""桌面端 IPC 工作线程：后台 asyncio 循环 + Qt 信号桥接。"""
from __future__ import annotations

import asyncio
import threading

from PySide6.QtCore import QObject, Signal

from services.ipc.reconnecting import ReconnectingClient
from shared.enums import MessageType


class IpcWorker(QObject):
    """后台线程跑 asyncio 客户端，把连接状态与飞机状态转成 Qt 信号。"""

    connection_changed = Signal(bool, str)   # connected, detail
    state_received = Signal(object)          # AircraftState dict

    def __init__(self, host: str = "127.0.0.1", port: int = 4200) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, name="desktop-ipc", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """请求停止：置位标志并等待线程退出（receive 每 1s 超时检查，最多约 1s 退出）。"""
        self._running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=3.0)

    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._client_loop())
        finally:
            loop.close()

    async def _client_loop(self) -> None:
        client = ReconnectingClient(self._host, self._port)
        while self._running:
            if not await client.connect_with_retry():
                self.connection_changed.emit(False, "连接失败，重试中…")
                await asyncio.sleep(2.0)
                continue
            welcome = await client.hello()
            if welcome is None:
                self.connection_changed.emit(False, "握手失败")
                await asyncio.sleep(2.0)
                continue
            summary = welcome.payload.get("state_summary", {})
            self.connection_changed.emit(True, f"事件数 {summary.get('event_count', 0)}")
            while self._running:
                try:
                    msg = await asyncio.wait_for(client.client.receive(), timeout=1.0)
                except TimeoutError:
                    continue  # 每 1s 醒来一次，重新检查 self._running
                if msg is None:
                    break
                if msg.type == MessageType.AIRCRAFT_STATE_UPDATED:
                    self.state_received.emit(msg.payload.get("state"))
            await client.client.close()
            self.connection_changed.emit(False, "连接断开")
            await asyncio.sleep(1.0)
