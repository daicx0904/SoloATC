# IPC 协议

## 传输
- localhost TCP，**JSON Lines**（每条消息一行 JSON）。
- 未来可迁 WebSocket，但协议语义不变。

## 握手与协商
1. 客户端连上后发 `HELLO`（含 protocol_version、client_type、client_id）。
2. 服务端回 `WELCOME`（含 accepted_version、server_time、snapshot）。
3. 版本不匹配 → `ERROR`（code=version_mismatch），客户端可降级重试。

## 消息结构（通用）
```json
{
  "id": "<uuid>",
  "type": "ATC_REQUEST",
  "ts_sim": 0.0,
  "ts_mono": 123456.7,
  "payload": { }
}
```
- `id`：消息唯一 ID（去重）。
- `ts_sim`：模拟器时间（秒，可被暂停/加速影响）。
- `ts_mono`：系统单调时间（毫秒级，用于超时/新鲜度）。

## 请求/响应关联
请求消息带 `id`；响应在 payload 里带 `reply_to`（原请求 id）。超时未响应 → 客户端重试或判错。

## 消息类型（初版）
```text
HELLO
WELCOME
HEARTBEAT
AIRCRAFT_STATE_UPDATED
FLIGHT_PHASE_CHANGED
FLIGHT_PLAN_SUBMITTED
ATC_REQUEST
CLEARANCE_PROPOSED
CLEARANCE_ISSUED
CLEARANCE_ACKNOWLEDGED
READBACK_RECEIVED
CLEARANCE_REJECTED
ATC_MESSAGE_RECEIVED
SIMULATOR_PAUSED
SIMULATOR_RESUMED
SESSION_STARTED
SESSION_ENDED
ERROR
```
所有消息必须有明确 Schema（Pydantic）。

## 心跳 / 超时 / 重连
- 双方定时发 `HEARTBEAT`；超时未收到 → 判定对端断开。
- 客户端指数退避重连；重连后重新 HELLO + 快照。

## 去重 / 快照恢复
- 服务端按 `id` 去重（保留最近 N 条 id）。
- 快照恢复：重连后客户端发当前 offset/已知状态，服务端回 `WELCOME` 携带最新 Session 快照与 AircraftState。

## 时间语义
- **simulator time**：飞行逻辑与事件顺序。
- **system monotonic time**：网络超时、新鲜度、性能计量。
两者必须区分（spec §6.1）。
