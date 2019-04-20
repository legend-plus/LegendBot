import struct

from packets.packet import Packet


class MoveAndFacePacket(Packet):

    name: str = "Move And Face"
    id: int = -6

    def __init__(self, x: int, y: int, facing: int):
        super().__init__()
        self.x = x
        self.y = y
        self.facing = facing

    @classmethod
    def decode(cls, data: bytes):
        x, y, facing = struct.unpack(">llB", data)
        return cls(x, y, facing)

    def encode(self) -> bytes:
        return struct.pack(">llB", self.x, self.y, self.facing)
