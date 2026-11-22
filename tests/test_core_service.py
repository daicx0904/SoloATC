"""CoreService 端到端测试。"""
import asyncio
import time
from uuid import uuid4

from core.service import CoreService
from services.ipc.client import IPCClient
from services.ipc.message import Message
from shared.enums import MessageType
from shared.schemas import AircraftState


def test_core_records_aircraft_state(tmp_path):
    async def scenario():
        core = CoreService(event_store_path=tmp_path / "events.jsonl", host="127.0.0.1", port=0)
        received = []
        core.bus.subscribe(MessageType.AIRCRAFT_STATE_UPDATED.value, lambda e: received.append(e))
        await core.start()

        client = IPCClient("127.0.0.1", core.server.bound_port)
        await client.connect()
        await client.send(Message(id=uuid4().hex, type=MessageType.HELLO, payload={}))
        await client.receive()  # WELCOME

        state = AircraftState(
            callsign="CES1234", latitude=40.0, longitude=116.0,
            altitude_msl_ft=1000.0, indicated_altitude_ft=1000.0,
            heading_deg=0.0, track_deg=0.0, groundspeed_kt=0.0,
            vertical_speed_fpm=0.0, on_ground=True, gear_down=True,
            flaps_ratio=0.0, timestamp=time.time(), groundspeed_valid=True,
        )
        await client.send(Message(
            id=uuid4().hex, type=MessageType.AIRCRAFT_STATE_UPDATED,
            ts_mono=time.monotonic(), payload={"state": state.model_dump(), "source": "mock"},
        ))
        await asyncio.sleep(0.2)
        await client.close()
        await core.stop()

        assert len(received) == 1
        assert received[0].event_type == MessageType.AIRCRAFT_STATE_UPDATED.value
        stored = core.store.load()
        assert len(stored) == 1
        assert stored[0].payload["state"]["callsign"] == "CES1234"

    asyncio.run(scenario())
