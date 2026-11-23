"""BridgeSender 线程化发送器测试。"""
import socket
import threading

from adapters.xplane.bridge import BridgeSender


def test_bridge_sender_delivers_json_line():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    received: dict = {}

    def accept():
        conn, _ = srv.accept()
        received["data"] = conn.recv(65536).decode("utf-8")
        conn.close()

    t = threading.Thread(target=accept, daemon=True)
    t.start()

    sender = BridgeSender("127.0.0.1", port)
    sender.start()
    sender.send({"type": "TEST", "payload": {"x": 1}})
    t.join(timeout=3.0)
    sender.stop()
    srv.close()

    assert received.get("data", "").strip() == '{"type": "TEST", "payload": {"x": 1}}'
