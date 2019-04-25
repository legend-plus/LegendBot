import struct
import uuid

from entities import Entity
from legendutils import ChatMessage, World
from packets.packet import Packet


class EntityMovePacket(Packet):

    name: str = "Entity Move"
    id: int = 9

    def __init__(self, entity_uuid: uuid.UUID, x: int, y: int, facing: int):
        super().__init__()
        self.x: int = x
        self.y: int = y
        self.entity_uuid: uuid.UUID = entity_uuid
        self.facing: int = facing

    @classmethod
    def decode(cls, data: bytes):
        pos_x, pos_y = struct.unpack(">ll", data[0:8])
        facing: int = data[8]
        entity_uuid: uuid.UUID = uuid.UUID(data[9:41].decode("utf-8"))
        return cls(entity_uuid, pos_x, pos_y, facing)

    def encode(self) -> bytes:
        output = b''

        output += struct.pack(">ll", self.x, self.y)
        output += struct.pack(">B", self.facing)
        output += self.entity_uuid.hex.encode("utf-8")
        return output
