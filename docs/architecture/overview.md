# SoloATC 架构总览

## 定位
X-Plane 12 单人 AI ATC 系统。不是语音播报插件，也不是按飞机位置随机生成指令的 AI，而是拥有**独立飞行状态管理、管制决策、规则验证、许可生命周期、冲突检测、事件记录**的系统。

## 核心原则
1. ATC 决策由**确定性规则引擎**负责。
2. AI（语音/自然语言）只负责理解与表达，**不能直接决定有效管制许可**。
3. 所有许可必须经过验证。
4. 所有客户端共享同一个 Core 与 Flight Session。
5. 核心业务逻辑**不得直接依赖 X-Plane SDK**。
6. ATC 只发布许可与监控执行，**不直接操纵飞机**。
7. 重要状态变化与决策都记录为事件。
8. 相同输入/规则版本/事件序列 → 可复现决策。
9. 预留多机场/全球规则/AI Traffic。
10. 第一阶段优先可靠、可测、可扩展，而非功能数量。

## 架构风格
**Modular Monolith + Event-Driven**。早期不做微服务。

## 进程结构

```
┌─────────────────────────────┐
│       Desktop Client        │
│          PySide6            │
└──────────────┬──────────────┘
               │ Local IPC (TCP + JSON Lines)
┌──────────────▼──────────────┐
│        SoloATC Core         │
│ Session / Controllers /     │
│ Rules / Clearance /         │
│ Navigation / Traffic /      │
│ Event System                │
└──────────────┬──────────────┘
               │ Local IPC (TCP + JSON Lines)
┌──────────────▼──────────────┐
│       X-Plane Bridge        │
│         XPPython3           │
└──────────────┬──────────────┘
               │ DataRefs / Commands
           X-Plane 12
```

辅助服务：Voice Service、Storage Service、Navigation Data Importer。

## 模块职责
- **Core**：独立进程，Headless 可运行。会话/阶段/管制员/规则/许可/导航/交通/事件/IPC Server。
- **X-Plane Bridge**：只读 DataRef、监听 Command、采集 AircraftState、检测暂停/加速/重载、发快照、收相关事件。Flight Loop 内禁止重活。
- **Desktop Client**：主操作界面（Flight Strip / Radio / Clearance / Comm Log / Aircraft Monitor / Navigation / Debug Console）。
- **规则引擎**：许可验证、高度/空域/RVSM/SID/STAR/进近限制、跑道占用、冲突检测、滑行限制、阶段校验。产出 `RuleResult`。

## 目录结构
见 spec §14。模块职责清晰，不为形式建空目录。
