import asyncio
import socket
import struct
import sys


class Server:
    def __init__(self, config):
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.config["ip"], self.config["port"]))
        self.sock.listen(10)
        self.sock.setblocking(False)
        self.sock.settimeout(15)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.run_server())

    async def handle_client(self, client):
        request = None
        print("Client connected")
        while request != 'quit':
            msg_len = await self.loop.sock_recv(client, 4)
            if not msg_len:
                continue
            msg_len = struct.unpack('>I', msg_len)[0]
            packet = await self.loop.sock_recv(client, msg_len)
            await self.loop.sock_sendall(client, packet)
        print("Client disconnected")
        client.close()

    async def run_server(self):
        while True:
            try:
                client, _ = await self.loop.sock_accept(self.sock)
                await self.loop.create_task(self.handle_client(client))
            except socket.timeout:
                pass

