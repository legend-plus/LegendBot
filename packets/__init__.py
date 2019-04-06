import struct

from bidict import bidict

from packets.packet import Packet

from packets.null_packet import NullPacket
from packets.ping_packet import PingPacket
from packets.pong_packet import PongPacket

packet_ids = bidict({
    "ping": -1,
    "null": 0,
    "pong": 1
})

packets = {
    -1: PingPacket,
    0: Packet,
    1: PongPacket
}


def create_packet(packet_id: int, data: bytes):
    packet_bytes = struct.pack(">I", len(data)+2) + struct.pack(">h", packet_id) + data
    return packet_bytes


def decode(packet_id: int, data: bytes):
    decoded_packet: Packet = packets[packet_id].decode(data)
    return decoded_packet
