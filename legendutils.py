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

    def get(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.world[min_y:max_y, min_x:max_x]

    def get_bump_map(self, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
        return self.bump_map[min_y:max_y, min_x:max_x]

    def collide(self, pos_x: int, pos_y: int) -> bool:
        return not self.bump_map[pos_y, pos_x] or (pos_x, pos_y) in self.entities

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


def to_hex(color_tuple: (int, int, int)) -> str:
    return "#" + bytes(color_tuple).hex()
