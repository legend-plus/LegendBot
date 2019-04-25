from abc import ABC, abstractmethod
import copy
from math import hypot

import items
import legendutils
from entities import Entity
from inventory import Inventory
from packets import EntityMovePacket, InvalidateCachePacket


class Game(Entity):
    ready: bool
    running: bool
    paused: bool
    gui_options:  list
    chat_buffer: list
    dialogue_buffer: list
    gui_description: str

    def __init__(self, pos_x: int, pos_y: int, legend, username: str, user_id: str):

        from legend import Legend
        self.legend: Legend = legend

        self.running: bool = False
        self.started: bool = False

        self.username = username
        self.user_id = user_id
        user_data = self.legend.users.find_one({"user": str(user_id)})
        if not user_data:
            user_data = copy.deepcopy(self.legend.config["default_user"])
            user_data["user"] = str(user_id)
            self.legend.users.insert_one(user_data)
        super().__init__("player", pos_x, pos_y, 0, user_data["sprite"])
        self.data = user_data
        inv = [items.from_dict(inv_item, self.legend.base_items) for inv_item in self.data["inventory"]]
        self.player_inventory = Inventory(inv, self.legend.base_items, self.legend.config)
        self.data["inventory"] = self.player_inventory
        self.opened_inventory: Inventory = Inventory([], self.legend.base_items, self.legend.config)

    def chat(self, msg):
        for g in self.legend.games:
            dist = hypot(self.legend.games[g].data["pos_x"] - self.data["pos_x"],
                         self.legend.games[g].data["pos_y"] - self.data["pos_y"])
            if dist <= self.legend.chat_radius:
                self.legend.games[g].add_msg(legendutils.ChatMessage(self.username,
                                                                     msg, self.user_id), self.data["pos_x"], self.data["pos_y"])

    def move(self, x: int, y: int, force: bool = False) -> bool:
        from directgame import DirectGame
        if self.running and self.legend.world.height > y >= 0 and self.legend.world.width > x >= 0:
            if force or not self.legend.world.collide(x, y):
                if self.legend.world.get_portal(x, y):
                    destination_portal = self.legend.world.get_portal(x, y)
                    self.data["pos_x"] = destination_portal["to_x"]
                    self.data["pos_y"] = destination_portal["to_y"]
                else:
                    if self.legend.world.can_trigger_encounters(x, y):
                        self.data["pos_x"] = x
                        self.data["pos_y"] = y
                        pass  # encounter =
                    else:
                        self.data["pos_x"] = x
                        self.data["pos_y"] = y
                for game in self.legend.games.values():
                    if isinstance(game, DirectGame) and self.uuid in game.entity_cache:
                        if self.data["pos_x"] - self.legend.config["entity_radius"] < game.data["pos_x"] < \
                                self.data["pos_x"] + self.legend.config["entity_radius"] and \
                                self.data["pos_y"] - self.legend.config["entity_radius"] < game.data["pos_y"] < \
                                self.data["pos_y"] + self.legend.config["entity_radius"]:
                            move_packet = EntityMovePacket(self.uuid, self.data["pos_x"], self.data["pos_y"], self.facing)
                            game.connection.send_packet(move_packet)
                        else:
                            # INVALIDATE_CACHE
                            invalidate_cache_packet = InvalidateCachePacket(self.uuid)
                            game.connection.send_packet(invalidate_cache_packet)
                            game.entity_cache.remove(self.uuid)
                return True
            else:
                if self.legend.world.get_entity(x, y):
                    entity = self.legend.world.get_entity(x, y)
                    if entity.interactable:
                        entity.interact(self)
                return False
        else:
            return False

    @abstractmethod
    def gui_interact(self, choice: int) -> None:
        pass

    @abstractmethod
    def add_msg(self, msg: legendutils.ChatMessage, x, y) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self, reason: str = None) -> bool:
        pass
