from datetime import datetime
import uuid
from typing import List, Dict


class ChatMessage:
    def __init__(self, author, discriminator, message):
        self.author = author
        self.discriminator = discriminator
        self.message = message[0:140]
        self.time = datetime.utcnow()
        self.uuid = uuid.uuid4().hex

    def __eq__(self, other):
        if isinstance(other, ChatMessage) and other.uuid == self.uuid:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class View:
    def __init__(self, view, min_x, max_x, min_y, max_y):
        self.view = view
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y


class World:
    def __init__(self, world, bump_map, portals, entities):
        self.height = len(world)
        self.width = len(world[0])
        self.world = world
        self.bump_map = bump_map
        self.portals = portals
        self.entities = entities  # type: Dict[(int, int), entities.Entity]

    def get(self, min_x: int, max_x: int, min_y: int, max_y: int):
        return self.world[min_y:max_y, min_x:max_x]

    def get_bump_map(self, min_x: int, max_x: int, min_y: int, max_y: int):
        return self.bump_map[min_y:max_y, min_x:max_x]

    def collide(self, pos_x: int, pos_y: int):
        return not self.bump_map[pos_y, pos_x]

    def get_portal(self, pos_x: int, pos_y: int):
        if (pos_x, pos_y) in self.portals:
            return self.portals[(pos_x, pos_y)]
        else:
            return False


def to_hex(color_tuple: (int, int, int)) -> str:
    return "#" + bytes(color_tuple).hex()