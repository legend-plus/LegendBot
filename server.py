import asyncio
import asyncore
from bidict import bidict
import socket
import struct
import sys
from threading import Thread

import packets
from legend import Legend
from packets import Packet, PingPacket, PongPacket, LoginPacket


class ClientHandler(asyncore.dispatcher_with_send):
        def __init__(self, sock=None, map=None, legend=None):
            super().__init__(sock, map)
            self.legend: Legend = legend

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

            if packet_type == PingPacket:
                packet: PingPacket
                response = PongPacket(packet.msg)
                self.send_packet(response)
            elif packet_type == LoginPacket:
                packet: LoginPacket
                packet.access_token
                # TODO: Use packet.access_token to verify user.


class Server(asyncore.dispatcher):
    def __init__(self, config, loop, legend: Legend):
        print("Starting Server")
        asyncore.dispatcher.__init__(self)
        print("Init")
        self.legend: Legend = legend
        self.config = config
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket creating, setting reuse")
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
