import struct

from packets.packet import Packet


class JoinGamePacket(Packet):

    name: str = "Join Game"
    id: int = -3

    def __init__(self):
        super().__init__()

    @classmethod
    def decode(cls, data: bytes):
        return cls()

    def encode(self) -> bytes:
        return b''
