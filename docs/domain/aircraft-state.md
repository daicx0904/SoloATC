# AircraftState 领域模型

统一、标准化的飞机状态。Core 只能使用 AircraftState，**不得**直接读 X-Plane DataRef。

## 字段（初版）
```python
class AircraftState:
    callsign: str
    latitude: float
    longitude: float
    altitude_msl_ft: float        # 气压高度(MSL)
    indicated_altitude_ft: float  # 指示高度
    heading_deg: float            # 机头航向
    track_deg: float              # 航迹
    groundspeed_kt: float
    vertical_speed_fpm: float
    on_ground: bool
    gear_down: bool
    flaps_ratio: float
    timestamp: float              # 采样时间
    groundspeed_valid: bool
```

## 关键区分（务必）
- **Heading vs Track**：heading 是机头指向，track 是实际航迹（受风影响）。
- **MSL vs Indicated**：高度基准、气压设置、过渡高度/过渡高度层都要考虑。
- **Simulator Time vs System Time**：飞行逻辑用 sim time，网络/新鲜度用 monotonic time。

## 数据质量
- **有效性**：DataRef 缺失/NaN → 字段标 invalid。
- **新鲜度**：超过阈值未更新的状态标记 stale，规则引擎不得基于 stale 状态做决策。
- **单位换算**：在 Bridge 侧统一换算到标准单位，Core 只认标准单位。

## 异常场景
- **模拟器暂停**：状态冻结，时间戳停更；恢复后继续。
- **时间加速**：sim time 快进，需据此判断新鲜度与事件顺序。
- **飞机重载**：Bridge 上报 reload，Core 丢弃旧状态。
- **缺失 DataRef**：Bridge 标 invalid 并上报告警，不静默伪造。

## 归属
- 真实 X-Plane DataRef 采集在 `adapters/xplane`。
- ToLiss 专用 DataRef 在 `adapters/aircraft/toliss`，不污染通用逻辑。
