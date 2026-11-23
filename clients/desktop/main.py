"""SoloATC 桌面客户端入口。"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

from clients.desktop.ipc_worker import IpcWorker


class MainWindow(QMainWindow):
    def __init__(self, host: str = "127.0.0.1", port: int = 4200) -> None:
        super().__init__()
        self.setWindowTitle("SoloATC Desktop")
        self.resize(420, 260)

        self._status_label = QLabel("未连接")
        self._aircraft_label = QLabel("等待飞机状态…")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("连接状态:"))
        layout.addWidget(self._status_label)
        layout.addWidget(QLabel("飞机状态:"))
        layout.addWidget(self._aircraft_label)
        self.setCentralWidget(central)

        self._worker = IpcWorker(host, port)
        self._worker.connection_changed.connect(self._on_connection)
        self._worker.state_received.connect(self._on_state)
        self._worker.start()

    def _on_connection(self, connected: bool, detail: str) -> None:
        color = "#2e7d32" if connected else "#c62828"
        self._status_label.setStyleSheet(f"color: {color}")
        self._status_label.setText(("已连接 · " if connected else "未连接 · ") + detail)

    def _on_state(self, state: dict) -> None:
        self._aircraft_label.setText(
            f"{state.get('callsign')}  高度 {state.get('altitude_msl_m')} m  "
            f"地速 {state.get('groundspeed_kt')} kt"
        )

    def closeEvent(self, event) -> None:
        self._worker.stop()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
