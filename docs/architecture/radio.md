# 无线电与 ATIS 设计（规划，待实现）

> 状态：**规划**。实现依赖 v0.2.0（FlightSession）+ v0.6.0（语音）。本文只定方向与数据模型。

## 目标
- 与机模无线电面板（COM1/COM2）连动。
- 玩家能调到正确管制频率，并按阶段切换（Ground→Tower→Departure→Center→Approach）。
- 能正确收听 ATIS。
- 双语 ATIS（中文/英文各占一频率）。

## 频率模型
每个机场定义一组频率（存机场数据）：
`ATIS / DELIVERY / GROUND / TOWER / DEPARTURE / APPROACH / CENTER`
每项 = 服务类型 + 频率值 +（ATIS 专用）语言。

FlightSession 的当前阶段 → 映射到「当前应联系的服务/频率」。
ATC 指令里带频率（"Contact Tower on 118.100"）。

## 与机模无线电面板连动
- Bridge 读 COM1/COM2 频率 DataRef（**待验证**：`sim/cockpit2/radios/actuators/com1_frequency_hz` 等）。
- Core 记录玩家当前调谐频率，校验是否在正确频率。
- 不在正确频率 → 不响应 / 提示"需要在 XXX.XXX 频率"。
- Desktop 的 Radio 面板可显示/设置频率，与机模双向同步（写 DataRef）。

## ATIS
- 自动循环广播：天气、跑道、QNH、风、运行提示等。
- 内容由 Core 从模拟器天气 + 机场数据生成。
- 玩家调到 ATIS 频率 → 听到（TTS，v0.6.0）/ 看到（文字字幕）。
- ATIS 代码（字母 A/B/C…）随内容更新递增。

## 双语 ATIS（规划，后期决定是否实现）
- 一个机场可有多个 ATIS 版本，各占一频率、各一种语言。
- 例：ZUGY D-ATIS(English) 126.825 / D-ATIS(Chinese) 127.050。
- 同一数据源，按语言模板（英文模板 / 中文模板）生成内容。

## 数据模型（草案）
```python
class RadioFrequency(BaseModel):
    airport: str
    service: str           # ATIS/DELIVERY/GROUND/TOWER/DEPARTURE/APPROACH/CENTER
    frequency_mhz: float
    language: str | None   # ATIS 专用：'en' / 'zh'

class AtisVersion(BaseModel):
    language: str
    frequency_mhz: float
    text: str

class Atis(BaseModel):
    airport: str
    code: str              # A/B/C…
    versions: list[AtisVersion]
```

## 阶段 → 频率映射（示意）
```text
PREFLIGHT / CLEARANCE   → DELIVERY
PUSHBACK / TAXI         → GROUND
TAKEOFF                 → TOWER
DEPARTURE               → DEPARTURE
CLIMB / CRUISE / DESCENT→ CENTER
ARRIVAL / APPROACH      → APPROACH
LANDING / ROLLOUT/TAXI_IN → TOWER / GROUND
```

## 待验证（spec §18.5）
- COM 频率 DataRef 名称与读写方式。
- ToLiss A320neo 是否直接暴露 COM 频率 DataRef（或经通用 DataRef）。
- ATIS 语音由 TTS 生成；双语模板具体措辞。
