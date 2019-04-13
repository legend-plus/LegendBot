import struct

from bidict import bidict

from packets.packet import Packet

from packets.null_packet import NullPacket

from packets.client.ping_packet import PingPacket
from packets.client.login_packet import LoginPacket
from packets.client.join_game_packet import JoinGamePacket
from packets.client.request_world_packet import RequestWorldPacket

from packets.server.pong_packet import PongPacket
from packets.server.login_result_packet import LoginResultPacket
from packets.server.world_packet import WorldPacket

packet_ids = bidict({
    "request_world": -4,
    "join_game": -3,
    "login": -2,
    "ping": -1,
    "null": 0,
    "pong": 1,
    "login_result": 2,
    "world": 3
})

packets = {
    -4: RequestWorldPacket,
    -3: JoinGamePacket,
    -2: LoginPacket,
    -1: PingPacket,
    0: Packet,
    1: PongPacket,
    2: LoginResultPacket,
    3: WorldPacket
}


def create_packet(packet_id: int, data: bytes):
    packet_bytes = struct.pack(">I", len(data)+2) + struct.pack(">h", packet_id) + data
    return packet_bytes


def decode(packet_id: int, data: bytes):
    decoded_packet: Packet = packets[packet_id].decode(data)
    return decoded_packet
