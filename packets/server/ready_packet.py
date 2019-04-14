import struct

from packets.packet import Packet


class ReadyPacket(Packet):

    name: str = "Ready"
    id: int = 4

    def __init__(self):
        super().__init__()

    @classmethod
    def decode(cls, data: bytes):
        return cls()

    def encode(self) -> bytes:
        return b''
