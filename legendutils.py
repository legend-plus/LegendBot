from datetime import datetime
import uuid
from typing import List, Dict, Optional
import entities
import numpy as np


class ChatMessage:
    def __init__(self, author: str, discriminator: str, message: str):
        self.author = author  # type: str
        self.discriminator = discriminator  # type: str
        self.message = message[0:140]  # type: str
        self.time = datetime.utcnow()  # type: datetime
        self.uuid = uuid.uuid4().hex  # type: uuid

    def __eq__(self, other) -> bool:
        if isinstance(other, ChatMessage) and other.uuid == self.uuid:
            return True
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class View:
    def __init__(self, view: np.ndarray, min_x: int, max_x: int, min_y: int, max_y: int):
        self.view = view  # type: np.ndarray
        self.min_x = min_x  # type: int
        self.max_x = max_x  # type: int
        self.min_y = min_y  # type: int
        self.max_y = max_y  # type: int


class World:
    def __init__(self, world: np.ndarray, bump_map: np.ndarray, portals, entities: Dict[(int, int), entities.Entity]):
        self.height = len(world)  # type: int
        self.width = len(world[0])  # type: int
        self.world = world  # type: np.ndarray
        self.bump_map = bump_map  # type: np.ndarray
        self.portals = portals  # type: Dict[(int, int), List[int, int, int, int]]
        self.entities = entities  # type: Dict[(int, int), entities.Entity]

    def get(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.world[min_y:max_y, min_x:max_x]

    def get_bump_map(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.bump_map[min_y:max_y, min_x:max_x]

    def collide(self, pos_x: int, pos_y: int) -> bool:
        return not self.bump_map[pos_y, pos_x]

    def get_entity(self, pos_x: int, pos_y: int) -> Optional[entities.Entity]:
        if (pos_x, pos_y) in self.entities:
            return self.entities[(pos_x, pos_y)]
        else:
            return None

    def get_portal(self, pos_x: int, pos_y: int) -> Optional[List[int, int, int, int]]:
        if (pos_x, pos_y) in self.portals:
            return self.portals[(pos_x, pos_y)]
        else:
            return None


def to_hex(color_tuple: (int, int, int)) -> str:
    return "#" + bytes(color_tuple).hex()
