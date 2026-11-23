"""线程化 TCP 发送器：不阻塞 X-Plane Flight Loop。纯标准库。"""
from __future__ import annotations

import json
import logging
import queue
import socket
import threading

logger = logging.getLogger(__name__)

_SENTINEL = object()


class BridgeSender:
    """后台线程消费队列，把 dict 消息以 JSON Lines 发往 Core。

    Flight Loop 只调用 send()（入队，非阻塞）；真正 socket IO 在后台线程。
    连接失败时丢弃本次消息（下次自动重连），不阻塞模拟器。
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 4200) -> None:
        self.host = host
        self.port = port
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, name="soloatc-bridge", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._queue.put(_SENTINEL)
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def send(self, msg: dict) -> None:
        self._queue.put(msg)

    def _run(self) -> None:
        sock: socket.socket | None = None
        while self._running:
            item = self._queue.get()
            if item is _SENTINEL:
                break
            try:
                if sock is None:
                    sock = socket.create_connection((self.host, self.port), timeout=2.0)
                sock.sendall((json.dumps(item) + "\n").encode("utf-8"))
            except OSError:
                logger.warning("发送到 Core 失败（将重连）", exc_info=True)
                if sock is not None:
                    try:
                        sock.close()
                    except OSError:
                        logger.debug("关闭 socket 失败", exc_info=True)
                    sock = None
        if sock is not None:
            sock.close()
