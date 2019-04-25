import struct
import uuid

from entities import Entity
from legendutils import ChatMessage, World
from packets.packet import Packet


class EntityPacket(Packet):

    name: str = "Entity"
    id: int = 8

    def __init__(self, entity: Entity, x: int, y: int):
        super().__init__()
        self.x: int = x
        self.y: int = y
        self.entity = entity

    @classmethod
    def decode(cls, data: bytes):
        pos_x, pos_y = struct.unpack(">ll", data[0:8])
        entity_type: int = struct.unpack(">H", data[9:10])[0]
        facing: int = data[11]
        interactable: bool = data[12] == 1
        sprite_length: int = struct.unpack(">L", data[13:17])[0]
        sprite: str = data[17:17+sprite_length].decode("utf-8")
        entity_uuid: uuid.UUID = uuid.UUID(data[17+sprite_length:49+sprite_length].decode("utf-8"))

        if entity_type == 1:
            # TODO: NPC
            pass
            entity = Entity("entity", pos_x, pos_y, facing, sprite, interactable, entity_uuid)
        elif entity_type == 2:
            # TODO: Player
            pass
            entity = Entity("entity", pos_x, pos_y, facing, sprite, interactable, entity_uuid)
        else:
            entity = Entity("entity", pos_x, pos_y, facing, sprite, interactable, entity_uuid)
        return cls(entity, pos_x, pos_y)

    def encode(self) -> bytes:
        output = b''
        encoded_sprite = self.entity.sprite.encode("utf_8")

        output += struct.pack(">ll", self.x, self.y)

        if self.entity.entity_type == "npc":
            type_id = 1
        elif self.entity.entity_type == "player":
            type_id = 2
        else:
            type_id = 0
        output += struct.pack(">H", type_id)

        output += struct.pack(">B", self.entity.facing)
        output += b'\x01' if self.entity.interactable else b'\x00'
        output += struct.pack(">L", len(encoded_sprite))
        output += encoded_sprite
        output += self.entity.uuid.hex.encode("utf-8")
        return output
