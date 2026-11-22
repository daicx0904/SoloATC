# SoloATC

面向 X-Plane 12 的单人 AI ATC（空中交通管制）系统。

## 定位
不是语音播报插件，也不是随机生成指令的 AI：SoloATC 拥有独立的**飞行状态管理、管制决策、规则验证、许可生命周期、冲突检测、事件记录**能力。

## 核心原则
- ATC 决策由**确定性规则引擎**负责
- AI 只负责语音理解与表达，**不直接决定有效许可**
- 所有许可必须经过验证
- 核心业务逻辑不直接依赖 X-Plane SDK

## 当前状态
- 阶段：**M0 已完成**（架构文档 + 项目脚手架）
- 许可证：GPL v3
- 双平台：GitHub + Gitee（`git push origin` 一次推两个）

## 目录
- `docs/`：架构、进程、IPC 协议、领域模型、路线图
- `core/`：会话、规则、许可、导航、交通、事件
- `adapters/`：X-Plane / 机型 / 交通适配器
- `services/`：IPC / 语音 / 存储 / 导航数据
- `clients/`：桌面(PySide6) / 机内(XPPython3) / Web
- `shared/`：schema / 协议 / 枚举

## 开发
Python 3.12 + uv。路线图见 `docs/development/roadmap.md`。
