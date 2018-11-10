from typing import List

from entities import Entity

class Enemy(Entity):
    def __init__(self, pos_x: int, pos_y: int, tile: str, friendly_tile: str, enemy_tile: str):
        super().__init__("enemy", pos_x, pos_y, tile)
        self.friendly_tile = friendly_tile
        self.enemy_tile = enemy_tile


class Battle:
    def __init__(self, teams: List[List[Entity]]):
        self.teams = teams
