"""Mock 飞机状态提供者端到端测试。"""
import asyncio

from adapters.mock.provider import MockAircraftStateProvider
from core.service import CoreService
from shared.enums import MessageType


def test_mock_provider_sends_states(tmp_path):
    async def scenario():
        core = CoreService(event_store_path=tmp_path / "events.jsonl", host="127.0.0.1", port=0)
        await core.start()

        provider = MockAircraftStateProvider(
            host="127.0.0.1", port=core.server.bound_port, interval=0.01
        )
        await provider.run(steps=3)
        await provider.client.close()
        await asyncio.sleep(0.2)
        await core.stop()

        events = core.store.load()
        states = [e for e in events if e.event_type == MessageType.AIRCRAFT_STATE_UPDATED.value]
        assert len(states) == 3
        assert states[0].payload["state"]["callsign"] == "CES1234"

    asyncio.run(scenario())
