# SoloATC 开发路线图

优先级：**Correctness > Reliability > Maintainability > Extensibility > Visual Polish**

## 里程碑总览

| 里程碑 | 主题 | 核心交付 |
|---|---|---|
| M0 | 环境与架构 | 环境核验、6 份架构文档、项目脚手架、双平台仓库 |
| M1 (v0.1.0) | 基础 | 项目结构、Core 骨架、事件系统、AircraftState、IPC、Bridge/Desktop 骨架、Mock 数据源、测试 |
| M2 (v0.2.0) | 飞行会话 | Flight Session、FlightPlan、.fms 解析、XP12 导航数据读取、交叉验证、Flight Phase 状态机、基础 IFR 放行、许可生命周期、基础规则引擎 |
| M3 (v0.3.0) | 地面+塔台 | 地面管制、滑行路线（有向图）、Hold Short、跑道占用、塔台、起飞许可 |
| M4 (v0.4.0) | 离场+进近 | SID/STAR/APP/ILS、复飞状态机、备降 |
| M5 (v0.5.0) | 中国民航规则 | China Rule Profile、RVSM、中国 AIP 数据、中文通话用语、程序校验 |
| M6 (v0.6.0) | 语音 | PTT、STT(whisper.cpp)、TTS(Piper)、复诵校验、语音 Adapter |
| M7 (v0.7.0) | 机内客户端 | X-Plane overlay（ImGui）、基础 ATC 交互 |
| M8 (v0.8.0) | Web 客户端 | Vue3 远程监控/UI |
| M9 (v0.9.0) | AI Traffic | TrafficProvider、AI 流量集成、冲突检测、AI 飞机（X-CSL） |
| M10 (v1.0.0) | 稳定版 | 完整流程、数据校验、回放、稳定性、文档 |

## 关键验收点（每里程碑）
- **M1**：Core 可独立启动；Desktop 能连接；Bridge 能发状态；Core 收状态并记事件；断线检测/重连/快照恢复。
- **M2**：真实 .fms 能解析；与 XP12 导航数据交叉验证；冲突时按「XP12 优先」生成 ResolvedFlightPlan；可复现；差异可审计。
- **M3**：滑行路线合法性、跑道占用锁、冲突检测（单机 MVP）。
- **M4**：正常 ILS 进近、复飞、重新进近、备降。
- **M5**：RVSM/高度层/进离场校验符合中国民航规则。
- **M6**：语音→结构化请求→规则引擎；TTS 只读已校验指令；复诵错误识别。

## 阶段纪律（spec §18）
1. 增量开发，不一次性生成整个项目。
2. 架构先行：明确模块边界与接口后再写代码。
3. 不过度设计：先实现真实需要的功能。
4. 每个重要模块必须有文档。
5. API 不确定的一律标记「待验证」，不得虚构。
6. 确定性：相同输入/规则版本/事件序列 → 相同决策。
