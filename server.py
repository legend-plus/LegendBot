import asyncio
import asyncore
from bidict import bidict
import requests
import socket
import struct
import sys
from threading import Thread

import typing

import packets
from directgame import DirectGame
from legend import Legend
from packets import Packet, PingPacket, PongPacket, LoginPacket, LoginResultPacket, JoinGamePacket, RequestWorldPacket, \
    WorldPacket, ReadyPacket, MovePacket, PlayerPositionPacket, MoveAndFacePacket


class ClientHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock=None, map=None, legend=None):
        super().__init__(sock, map)
        self.legend: Legend = legend
        self.logged_in: bool = False
        self.user_id: str = None
        self.username: str = None
        self.game = None
        self.running = True
        ready = ReadyPacket(0)
        self.send_packet(ready)

    def send_packet(self, packet: Packet):
        packet_id: int = packet.id
        data: bytes = packet.encode()
        packet_bytes = packets.create_packet(packet_id, data)
        self.send(packet_bytes)

    def handle_read(self):
        # Get Packet Length
        msg_len = self.recv(4)
        if not msg_len:
            return
        msg_len = struct.unpack(">I", msg_len)[0]
        packet_contents = self.recv(msg_len)

        packet_id: int = struct.unpack(">h", packet_contents[0:2])[0]
        packet_data: bytes = packet_contents[2:]

        packet = packets.decode(packet_id, packet_data)
        packet_type = type(packet)

        # print("Received id " + str(packet_id) + "(" + str(packet_type) + ") len " + str(msg_len))

        if packet_type == PingPacket:
            packet: PingPacket
            response = PongPacket(packet.msg)
            self.send_packet(response)
            print("PONG \"" + packet.msg + "\"")
        elif packet_type == LoginPacket:
            packet: LoginPacket
            if not self.logged_in:
                headers = {
                    "User-Agent": "Legend Plus login bot v0.1",
                    "Authorization": "Bearer " + packet.access_token
                }
                r = requests.get("https://discordapp.com/api/users/@me", headers=headers)
                result = r.json()
                if "id" in result and "message" not in result:
                    # Successful login
                    response = LoginResultPacket(1, result["id"])
                    self.logged_in = True
                    self.username = result["username"] + "#" + result["discriminator"]
                    self.user_id = result["id"]
                    self.send_packet(response)
                else:
                    # Failed
                    response = LoginResultPacket(0)
                    self.send_packet(response)
            else:
                response = LoginResultPacket(2)
                self.send_packet(response)
        elif packet_type == JoinGamePacket:
            packet: JoinGamePacket
            if self.logged_in:
                if self.user_id in self.legend.games:
                    self.wait(self.legend.games[self.user_id].disconnect())
                    self.legend.games.pop(self.user_id)
                self.legend.games[self.user_id] = DirectGame(self, self.legend, self.user_id, self.username)
                self.wait(self.legend.games[self.user_id].start())
                self.game = self.legend.games[self.user_id]
            else:
                pass
        elif packet_type == RequestWorldPacket:
            packet: RequestWorldPacket
            if self.game.running:
                response = WorldPacket(self.legend.world.height,
                                       self.legend.world.width,
                                       self.legend.world.world_bytes,
                                       self.legend.world.world_byte_size,
                                       self.legend.world.bump_bytes,
                                       self.legend.world.bump_byte_size)
                self.send_packet(response)
            else:
                pass
        elif packet_type == MovePacket or packet_type == MoveAndFacePacket:
            packet: MovePacket
            if self.game.running:
                self.game.move(packet.x, packet.y)
                if self.game.data["pos_x"] != packet.x or self.game.data["pos_y"] != packet.y:
                    position_packet = PlayerPositionPacket(self.game.data["pos_x"], self.game.data["pos_y"])
                    self.send_packet(position_packet)
                if packet_type == MoveAndFacePacket:
                    packet: MoveAndFacePacket
                    self.game.facing = packet.facing

    def handle_close(self):
        self.running = False
        if self.logged_in and self.user_id in self.legend.games and type(self.legend.games[self.user_id]) == DirectGame:
            self.wait(self.legend.games[self.user_id].disconnect("Timeout"))
        super().handle_close()

    def wait(self, func):
        future = asyncio.run_coroutine_threadsafe(func, self.legend.server_loop)
        return future.result()


class Server(asyncore.dispatcher):
    def __init__(self, config, loop, legend: Legend):
        print("Starting Server")
        asyncore.dispatcher.__init__(self)
        print("Init")
        self.legend: Legend = legend
        self.config = config
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        print("Binding server to " + self.config["ip"] + ":" + str(self.config["port"]))
        self.bind((self.config["ip"], self.config["port"]))
        self.listen(10)

    def handle_accept(self):
        print("Handle Accept")
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print("Connection from " + str(addr))
            handler = ClientHandler(sock=sock, legend=self.legend)
