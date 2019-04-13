import struct

from packets.packet import Packet


class RequestWorldPacket(Packet):

    name: str = "Request World"
    id: int = -4

    def __init__(self):
        super().__init__()

    @classmethod
    def decode(cls, data: bytes):
        return cls()

    def encode(self) -> bytes:
        return b''
