import struct

from packets.packet import Packet


class ReadyPacket(Packet):

    name: str = "Ready"
    id: int = 4

    def __init__(self, code: int):
        super().__init__()
        self.code = code

    @classmethod
    def decode(cls, data: bytes):
        return cls(data[0])

    def encode(self) -> bytes:
        return struct.pack(">B", self.code)
