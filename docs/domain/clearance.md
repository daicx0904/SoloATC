# Clearance 领域模型

结构化许可。不是模糊的"altitude"字段，而是带明确语义的指令。

## 字段（初版）
```python
class Clearance:
    clearance_id: str
    controller: str
    callsign: str
    clearance_type: str
    parameters: dict
    valid_from: float
    expires_at: float
    status: str
    source_rule: str
```

## 生命周期
```text
PROPOSED → VALIDATED → ISSUED → ACKNOWLEDGED → EXECUTING → COMPLETED
                  ↓
              REJECTED
     （另有 EXPIRED / CANCELLED）
```

## 许可类型语义（不可混为一谈）
| 指令 | 语义 |
|---|---|
| Descend and Maintain FL120 | 降到并保持 FL120 |
| Descend to FL120 | 降到 FL120（一次性，后续再议） |
| At or Below FL120 | 不得高于 FL120 |
| Cross FIX at FL150 | 过 FIX 时高度 FL150 |
| Maintain 250 Knots Until Further Advised | 保持 250 节直到另行通知 |

## 必须区分的五个概念
1. **Published Procedures**：公布的进离场/进近程序。
2. **ATC Radar Vectors**：雷达引导航向/高度。
3. **Aircraft Performance**：飞机性能限制。
4. **ATC Clearance**：管制许可本身。
5. **Actual Aircraft State**：飞机实际状态。
这五者不得混淆；许可验证时逐层校验。

## 验证
- 每条许可经规则引擎验证后才可 ISSUED；`source_rule` 指向 Rule ID + 版本。
- AI/语音只能 PROPOSE，不能绕过规则引擎发布许可。
