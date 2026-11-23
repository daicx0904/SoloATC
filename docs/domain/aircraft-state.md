# AircraftState 领域模型

统一、标准化的飞机状态。Core 只能使用 AircraftState，**不得**直接读 X-Plane DataRef。

## 单位分层（三层，务必区分）
1. **原始层**：X-Plane DataRef 原生单位（米、米/秒等，混合）。
2. **规范层（本模型）**：ATC 引擎统一使用 —— **高度=米(m)，水平速度=节(kt)**。
3. **显示层**：按地区/Rule Profile 转换 —— 中国=米、km/h、km；美国=ft、kt、nm。

- Bridge 的 collector 只做 ①→②。
- 显示层（②→③）在 UI/表现层做，由 Rule Profile 驱动。

## 字段（规范单位）
```python
class AircraftState:
    callsign: str
    latitude: float
    longitude: float
    altitude_msl_m: float        # 米（MSL 气压高度）
    indicated_altitude_m: float  # 米（指示高度）
    heading_deg: float
    track_deg: float
    groundspeed_kt: float        # 节
    vertical_speed_mps: float    # 米/秒（fpm 派生字段后期加）
    on_ground: bool
    gear_down: bool
    flaps_ratio: float
    timestamp: float
    groundspeed_valid: bool
```

## 关键区分（务必）
- **Heading vs Track**：heading 是机头指向，track 是实际航迹（受风影响）。
- **MSL vs Indicated**：高度基准、气压设置、过渡高度/过渡高度层都要考虑。
- **Simulator Time vs System Time**：飞行逻辑用 sim time，网络/新鲜度用 monotonic time。

## 数据质量
- 有效性：DataRef 缺失/NaN → invalid。
- 新鲜度：超阈值 stale，规则引擎不得基于 stale 状态决策。
- 单位换算：Bridge 侧统一换算到规范单位。

## 异常场景
- 模拟器暂停 / 时间加速 / 飞机重载 / 缺失 DataRef（详见 spec §6.1）。

## 归属
- 真实 DataRef 采集在 `adapters/xplane`。
- ToLiss 专用 DataRef 在 `adapters/aircraft/toliss`，不污染通用逻辑。
