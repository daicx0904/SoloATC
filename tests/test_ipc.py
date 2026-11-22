"""IPC 收发测试。"""
import asyncio

from services.ipc.client import IPCClient
from services.ipc.message import Message
from services.ipc.server import IPCServer
from shared.enums import MessageType


def test_hello_welcome_roundtrip():
    async def scenario():
        server = IPCServer("127.0.0.1", 0)
        received = []

        async def handler(msg, writer):
            received.append(msg)
            if msg.type == MessageType.HELLO:
                await server.send(writer, Message(id="w1", type=MessageType.WELCOME, payload={}))

        server.set_message_handler(handler)
        await server.start()
        client = IPCClient("127.0.0.1", server.bound_port)
        await client.connect()
        await client.send(Message(id="h1", type=MessageType.HELLO, payload={}))
        reply = await client.receive()
        assert reply is not None and reply.type == MessageType.WELCOME
        assert len(received) == 1 and received[0].id == "h1"
        await client.close()
        await server.stop()

    asyncio.run(scenario())
