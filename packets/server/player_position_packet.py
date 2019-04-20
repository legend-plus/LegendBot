import struct

from packets.packet import Packet


class PlayerPositionPacket(Packet):

    name: str = "Player Position"
    id: int = 5

    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y

    @classmethod
    def decode(cls, data: bytes):
        x, y = struct.unpack(">ll", data)
        return cls(x, y)

    def encode(self) -> bytes:
        return struct.pack(">ll", self.x, self.y)
