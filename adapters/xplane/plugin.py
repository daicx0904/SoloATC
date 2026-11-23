"""SoloATC X-Plane Bridge 插件（XPPython3 v4）。

- 运行在 XPPython3 内嵌 Python 3.12，**纯标准库**（零第三方依赖）。
- 部署位置：<X-Plane>/Resources/plugins/PythonPlugins/（需把 adapters/xplane 包放上 XPPython3 的 sys.path）。
- 职责：Flight Loop 里轻量读 DataRef → 构建 AircraftState dict → 交给后台线程发送。
- 禁止在 Flight Loop 中做网络/重活（spec §5.2）。
"""
from __future__ import annotations

import time
from uuid import uuid4

from XPPython3 import xp

from adapters.xplane.bridge import BridgeSender
from adapters.xplane.collector import build_aircraft_state_dict

INTERVAL = 0.5
CORE_HOST = "127.0.0.1"
CORE_PORT = 4200
# 待实现：从机模尾号读取呼号
CALLSIGN = "N000SA"

# 待验证：以下 DataRef 名称需在 X-Plane 中用 DataRefTool 逐一核对（spec §18.5）
DATAREFS: dict[str, tuple[str, str]] = {
    "latitude": ("sim/flightmodel/position/latitude", "double"),
    "longitude": ("sim/flightmodel/position/longitude", "double"),
    "elevation_m": ("sim/flightmodel/position/elevation", "double"),
    "indicated_altitude_ft": ("sim/cockpit2/gauges/indicators/altitude_ft_pilot", "float"),
    "heading_deg": ("sim/flightmodel/position/psi", "float"),
    "track_deg": ("sim/flightmodel/position/hpath", "float"),
    "groundspeed_ms": ("sim/flightmodel/position/groundspeed", "float"),
    "vertical_speed_fpm": ("sim/flightmodel/position/vh_ind_fpm", "float"),
    "on_ground": ("sim/flightmodel/failures/onground_any", "int"),
    "gear_down": ("sim/cockpit2/controls/gear_handle_down", "int"),
    "flaps_ratio": ("sim/cockpit2/controls/flap_ratio", "float"),
}


class PythonInterface:
    def XPluginStart(self):
        self.Name = "SoloATC Bridge"
        self.Sig = "soloatc.bridge"
        self.Desc = "Collect aircraft state and forward to SoloATC Core over TCP"
        self._refs = {key: xp.findDataRef(name) for key, (name, _t) in DATAREFS.items()}
        self._warned: set[str] = set()
        self._sender = BridgeSender(CORE_HOST, CORE_PORT)
        self._sender.start()
        xp.registerFlightLoopCallback(self._flight_loop, INTERVAL, None)
        return self.Name, self.Sig, self.Desc

    def XPluginStop(self):
        xp.unregisterFlightLoopCallback(self._flight_loop, None)
        self._sender.stop()

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    def _flight_loop(self, since_last, elapsed_sim, counter, refcon):
        state = build_aircraft_state_dict(CALLSIGN, self._read_datarefs(), time.time())
        self._sender.send({
            "id": uuid4().hex,
            "type": "AIRCRAFT_STATE_UPDATED",
            "ts_sim": elapsed_sim,
            "ts_mono": time.monotonic(),
            "payload": {"state": state, "source": "xplane"},
        })
        return INTERVAL

    def _read_datarefs(self) -> dict:
        raw: dict = {}
        for key, (name, typ) in DATAREFS.items():
            ref = self._refs.get(key)
            if ref is None:
                if key not in self._warned:
                    xp.log(f"SoloATC: DataRef 未找到: {name}")
                    self._warned.add(key)
                raw[key] = 0
                continue
            if typ == "double":
                raw[key] = xp.getDatad(ref)
            elif typ == "float":
                raw[key] = xp.getDataf(ref)
            else:
                raw[key] = xp.getDatai(ref)
        return raw
