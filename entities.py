from interactions import Dialogue
import legendgame


class Entity:
    def __init__(self, entity_type: str, pos_x: int, pos_y: int, tile: str, interactable: bool = False):
        self.entity_type = entity_type  # type: str
        self.pos_x = pos_x  # type: int
        self.pos_y = pos_y  # type: int
        # tile is the emoji string, ex: <a:_:499435126908780554>
        self.tile = tile  # type: str
        self.interactable = interactable  # type: bool
        pass


class NPC(Entity):
    def __init__(self, entity_type: str, pos_x: int, pos_y: int, tile: str, dialogue: Dialogue):
        super().__init__(entity_type, pos_x, pos_y, tile, True)
        self.dialogue = dialogue  # type: Dialogue

    def interact(self, game: legendgame.LegendGame):
        self.dialogue.interact(game)
