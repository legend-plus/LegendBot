import numpy

import legendutils
import packets
import readline
import socket
import struct
import sys

from packets import WorldPacket

numpy.set_printoptions(threshold=sys.maxsize, linewidth=99999)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("192.95.22.236", 21321))
if len(sys.argv) == 1:
    print("Access Token: ")
    access_token = input()
else:
    access_token = sys.argv[1]

login_packet = packets.LoginPacket(access_token)
login_send = packets.create_packet(login_packet.id, login_packet.encode())
sock.send(login_send)
resp = sock.recv(9999999)
resp_packet = packets.decode(struct.unpack(">h", resp[4:6])[0], resp[6:])

request_packet = packets.RequestWorldPacket()
request_send = packets.create_packet(request_packet.id, request_packet.encode())
sock.send(request_send)
world_packet_data = sock.recv(99999999)
world_packet: WorldPacket = packets.decode(struct.unpack(">h", world_packet_data[4:6])[0], world_packet_data[6:])

the_world = legendutils.World.decode(world_packet.height,
                                     world_packet.width,
                                     world_packet.world,
                                     world_packet.world_word_size,
                                     world_packet.bump_world,
                                     world_packet.bump_word_size)
print("WORLD")
print(str(the_world.world))
