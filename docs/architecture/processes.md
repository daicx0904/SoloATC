# 进程与生命周期

## 进程清单
| 进程 | 技术 | 职责 |
|---|---|---|
| Core | Python (uv 3.12.10) | 业务核心，Headless 可运行，IPC Server |
| Desktop Client | PySide6 / Qt6 | 主 UI |
| X-Plane Bridge | XPPython3（内嵌 Py3.12） | 采集/注入模拟器状态 |
| Voice Service | whisper.cpp + Piper | STT / TTS（独立 Adapter） |
| Storage Service | SQLite | 事件持久化 |
| Navigation Data Importer | 离线工具 | AIP/航图 → SQLite |

## 通信边界
- Core ↔ Desktop：TCP JSON Lines。
- Core ↔ Bridge：TCP JSON Lines。
- Bridge 只与 X-Plane SDK 交互；Core/Desktop **不**接触 SDK。
- 客户端不得直接访问 Core 内部对象，一切经协议消息。

## 启动顺序
1. Core 启动，监听 IPC 端口，加载规则与导航数据。
2. Bridge 随 X-Plane 加载（XPPython3），连接 Core，HELLO/WELCOME 协商。
3. Desktop 连接 Core，订阅事件，请求当前快照。
4. 心跳维持连接；超时判死。

## 退出与故障恢复
- **Core 退出**：客户端检测断开，进入重连；重连成功后拉快照。
- **Core 重启**：事件日志持久化，可恢复 Session（故障恢复见 ipc.md 快照）。
- **插件重载 / 飞机重载**：Bridge 重新 HELLO，Core 以 aircraft reload 处理，清空陈旧 AircraftState。
- **客户端重连**：重协商协议版本 + 去重 + 快照恢复。
- **模拟器暂停/加速**：AircraftState 与事件带 sim time 与 monotonic time，判定数据新鲜度。
