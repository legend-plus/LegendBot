import asyncio
import asyncore
import socket
import struct
import sys
from threading import Thread


class ClientHandler(asyncore.dispatcher_with_send):
        def handle_read(self):
            #Get Packet Length
            msg_len = self.recv(4)
            if not msg_len:
                return
            msg_len = struct.unpack(">I", msg_len)[0]
            packet = self.recv(msg_len)
            self.send(packet)


class Server(asyncore.dispatcher):
    def __init__(self, config, loop):
        print("Starting Server")
        asyncore.dispatcher.__init__(self)
        print("Init")
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
            handler = ClientHandler(sock)
