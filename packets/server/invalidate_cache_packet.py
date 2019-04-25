import struct
import uuid

from entities import Entity
from legendutils import ChatMessage, World
from packets.packet import Packet


class InvalidateCachePacket(Packet):

    name: str = "Invalid Cache"
    id: int = 10

    def __init__(self, entity_uuid: uuid.UUID):
        super().__init__()
        self.entity_uuid: uuid.UUID = entity_uuid

    @classmethod
    def decode(cls, data: bytes):
        entity_uuid: uuid.UUID = uuid.UUID(data[0:32].decode("utf-8"))
        return cls(entity_uuid)

    def encode(self) -> bytes:
        output = b''
        output += self.entity_uuid.hex.encode("utf-8")
        return output
