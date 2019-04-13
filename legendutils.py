import numpy
import struct
from datetime import datetime
import uuid
from typing import List, Dict, Optional, Tuple
import entities
import numpy as np

from entities import Entity


class ChatMessage:
    def __init__(self, author: str, discriminator: str, message: str):
        self.author: str = author
        self.discriminator: str = discriminator
        self.message: str = message[0:140]
        self.time: datetime = datetime.utcnow()
        self.uuid: uuid = uuid.uuid4().hex

    def __eq__(self, other) -> bool:
        if isinstance(other, ChatMessage) and other.uuid == self.uuid:
            return True
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class View:
    def __init__(self, view: np.ndarray, min_x: int, max_x: int, min_y: int, max_y: int):
        self.view: np.ndarray = view
        self.min_x: int = min_x
        self.max_x: int = max_x
        self.min_y: int = min_y
        self.max_y: int = max_y


class World:
    def __init__(self, world: np.ndarray, bump_map: np.ndarray, portals, entities: Dict[Tuple[int, int], entities.Entity]):
        self.height: int = len(world)
        self.width: int = len(world[0])
        self.world: np.ndarray = world
        self.bump_map: np.ndarray = bump_map
        self.portals: Dict[Tuple[int, int], Dict[str, int]] = portals
        self.entities: Dict[Tuple[int, int], Entity] = entities
        self.world_bytes: bytes = b''
        self.world_byte_size: int = 1
        self.get_world_bytes()
        self.bump_bytes: bytes = b''
        self.bump_byte_size: int = 1
        self.get_bump_bytes()

    def get(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.world[min_y:max_y, min_x:max_x]

    def get_bump_map(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.bump_map[min_y:max_y, min_x:max_x]

    def collide(self, pos_x: int, pos_y: int) -> bool:
        return not self.bump_map[pos_y, pos_x] or (pos_x, pos_y) in self.entities

    def can_trigger_encounters(self, pos_x: int, pos_y: int) -> bool:
        return self.bump_map[pos_y, pos_x] == 2

    def get_entity(self, pos_x: int, pos_y: int) -> Optional[entities.Entity]:
        if (pos_x, pos_y) in self.entities:
            return self.entities[(pos_x, pos_y)]
        else:
            return None

    def get_portal(self, pos_x: int, pos_y: int) -> Optional[Dict[str, int]]:
        if (pos_x, pos_y) in self.portals:
            return self.portals[(pos_x, pos_y)]
        else:
            return None

    def reload(self, world: np.ndarray = None,
               bump_map: np.ndarray = None,
               portals: Dict[Tuple[int, int], Dict[str, int]] = None,
               entities: Dict[Tuple[int, int], entities.Entity] = None):
        if world is not None:
            self.world = world
            self.get_world_bytes()
        if bump_map is not None:
            self.bump_map = bump_map
            self.get_bump_bytes()
        if portals is not None:
            self.portals = portals
        if entities is not None:
            self.entities = entities

    def get_world_bytes(self):
        output: bytes = b''
        max_value: int = self.world.max()
        if max_value <= (2**8) - 1:
            self.world_byte_size = 1
        elif max_value <= (2**16) - 1:
            self.world_byte_size = 2
        elif max_value <= (2**32) - 1:
            self.world_byte_size = 4
        else:
            return
        for y in range(self.height):
            for x in range(self.width):
                fmt = ">"
                if self.world_byte_size == 1:
                    fmt += "B"
                elif self.world_byte_size == 2:
                    fmt += "H"
                elif self.world_byte_size == 4:
                    fmt += "L"
                output += struct.pack(fmt, self.world[y, x])
        self.world_bytes = output

    def get_bump_bytes(self):
        output: bytes = b''
        max_value: int = self.bump_map.max()
        if max_value <= (2**8) - 1:
            self.bump_byte_size = 1
        elif max_value <= (2**16) - 1:
            self.bump_byte_size = 2
        elif max_value <= (2**32) - 1:
            self.bump_byte_size = 4
        else:
            return
        for y in range(self.height):
            for x in range(self.width):
                fmt = ">"
                if self.bump_byte_size == 1:
                    fmt += "B"
                elif self.bump_byte_size == 2:
                    fmt += "H"
                elif self.bump_byte_size == 4:
                    fmt += "L"
                output += struct.pack(fmt, self.bump_map[y, x])
        self.bump_bytes = output

    @classmethod
    def decode(cls, height: int, width: int, world: bytes, world_word_size: int, bump_world: bytes, bump_word_size: int):
        output_world = []
        output_row = []
        x, y = (0, 0)
        for pixel in range(0, len(world), world_word_size):
            x += 1
            fmt = ">"
            if world_word_size == 1:
                fmt += "B"
            elif world_word_size == 2:
                fmt += "H"
            elif world_word_size == 4:
                fmt += "L"
            pixel_value = struct.unpack(fmt, world[pixel:pixel+world_word_size])[0]
            output_row.append(pixel_value)
            if x == width:
                y += 1
                x = 0
                output_world.append(output_row)
                output_row = []
        output_world = numpy.array(output_world)

        x, y = (0, 0)
        output_bump_world = []
        output_row = []
        for pixel in range(0, len(bump_world), bump_word_size):
            x += 1
            fmt = ">"
            if bump_word_size == 1:
                fmt += "B"
            elif bump_word_size == 2:
                fmt += "H"
            elif bump_word_size == 4:
                fmt += "L"
            pixel_value = struct.unpack(fmt, world[pixel:pixel + bump_word_size])[0]
            output_row.append(pixel_value)
            if x == width:
                y += 1
                x = 0
                output_bump_world.append(output_row)
                output_row = []
        output_bump_world = numpy.array(output_bump_world)

        return cls(output_world, output_bump_world, {}, {})


def to_hex(color_tuple: (int, int, int)) -> str:
    return "#" + bytes(color_tuple).hex()
