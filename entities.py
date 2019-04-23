import interactions
import uuid


class Entity:

    def __init__(self, entity_type: str, pos_x: int, pos_y: int, facing: int, sprite: str, interactable: bool = False,
                 entity_uuid: uuid.UUID = None):
        self.entity_type: str = entity_type
        self.data = {
            "pos_x": pos_x,
            "pos_y": pos_y
        }
        self.facing: int = facing
        # tile is the emoji string, ex: <a:_:499435126908780554>
        self.sprite: str = sprite
        self.interactable: bool = interactable
        if entity_uuid is None:
            self.uuid = uuid.uuid4()
        else:
            self.uuid = entity_uuid
        pass


class NPC(Entity):

    def __init__(self, pos_x: int, pos_y: int, facing: int, sprite: str, dialogue: interactions.Dialogue):
        entity_type = "npc"
        super().__init__(entity_type, pos_x, pos_y, facing, sprite, True)
        self.dialogue: interactions.Dialogue = dialogue

    def interact(self, session):
        self.dialogue.interact(session)
