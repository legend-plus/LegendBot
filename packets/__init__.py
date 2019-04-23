import struct

from bidict import bidict

from packets.client.move_and_face_packet import MoveAndFacePacket
from packets.client.move_packet import MovePacket
from packets.client.send_message_packet import SendMessagePacket
from packets.packet import Packet

from packets.null_packet import NullPacket

from packets.client.ping_packet import PingPacket
from packets.client.login_packet import LoginPacket
from packets.client.join_game_packet import JoinGamePacket
from packets.client.request_world_packet import RequestWorldPacket
from packets.server.chat_packet import ChatPacket
from packets.server.disconnect_packet import DisconnectPacket
from packets.server.entity_packet import EntityPacket
from packets.server.player_position_packet import PlayerPositionPacket

from packets.server.pong_packet import PongPacket
from packets.server.login_result_packet import LoginResultPacket
from packets.server.ready_packet import ReadyPacket
from packets.server.world_packet import WorldPacket

packet_ids = bidict({
    "send_message": -7,
    "move_and_face": -6,
    "move": -5,
    "request_world": -4,
    "join_game": -3,
    "login": -2,
    "ping": -1,
    "null": 0,
    "pong": 1,
    "login_result": 2,
    "world": 3,
    "ready": 4,
    "player_position": 5,
    "disconnect": 6,
    "chat": 7,
    "entity": 8
})

packets = {
    -7: SendMessagePacket,
    -6: MoveAndFacePacket,
    -5: MovePacket,
    -4: RequestWorldPacket,
    -3: JoinGamePacket,
    -2: LoginPacket,
    -1: PingPacket,
    0: Packet,
    1: PongPacket,
    2: LoginResultPacket,
    3: WorldPacket,
    4: ReadyPacket,
    5: PlayerPositionPacket,
    6: DisconnectPacket,
    7: ChatPacket,
    8: EntityPacket
}


def create_packet(packet_id: int, data: bytes):
    packet_bytes = struct.pack(">I", len(data)+2) + struct.pack(">h", packet_id) + data
    return packet_bytes


def decode(packet_id: int, data: bytes):
    decoded_packet: Packet = packets[packet_id].decode(data)
    return decoded_packet
