class Item:
    def __init__(self, base: str = "item", sprite: str = None, item_type: str = None, name: str = None,
                 description: str = None):
        self.base = base
        if sprite is not None:
            self.sprite: str = sprite
        if item_type is not None:
            self.item_type: str = item_type
        if name is not None:
            self.name: str = name
        if description is not None:
            self.description: str = description

    def get_sprite(self, base_items):
        if hasattr(self, "sprite"):
            return self.sprite
        else:
            return base_items[self.base]["sprite"]

    def get_item_type(self, base_items):
        if hasattr(self, "item_type"):
            return self.item_type
        else:
            return base_items[self.base]["item_type"]

    def get_name(self, base_items):
        if hasattr(self, "name"):
            return self.name
        else:
            return base_items[self.base]["name"]

    def get_description(self, base_items):
        if hasattr(self, "description"):
            return self.description
        else:
            return base_items[self.base]["description"]


class Weapon(Item):
    def __init__(self, base: str = "item", sprite: str = None, item_type: str = None, name: str = None,
                 description: str = None, weapon_class: str = None,
                 damage: float = None, damage_type: str = None):
        super().__init__(base, sprite, item_type, name, description)
        if weapon_class is not None:
            self.weapon_class: str = weapon_class
        if damage is not None:
            self.damage: float = damage
        if damage_type is not None:
            self.damage_type: str = damage_type

    def get_damage(self, base_items):
        if hasattr(self, "damage"):
            return self.damage
        else:
            return base_items[self.base]["damage"]

    def get_damage_type(self, base_items):
        if hasattr(self, "damage_type"):
            return self.damage_type
        else:
            return base_items[self.base]["damage_type"]

    def get_weapon_class(self, base_items):
        if hasattr(self, "weapon_class"):
            return self.weapon_class
        else:
            return base_items[self.base]["weapon_class"]


def from_dict(item_dict: dict, item_bases: dict) -> Item:
    if ("item_type" in item_dict and item_dict["item_type"] == "weapon") or item_bases[item_dict["base"]]["item_type"]:
        return Weapon(
                      item_dict.get("base", "item"),
                      item_dict.get("sprite", None),
                      "weapon",
                      item_dict.get("name", None),
                      item_dict.get("description", None),
                      item_dict.get("weapon_class", None),
                      item_dict.get("damage", None),
                      item_dict.get("damage_type", None)
                      )
    else:
        return Item(
                    item_dict.get("base", None),
                    item_dict.get("sprite", None),
                    "misc",
                    item_dict.get("name", None),
                    item_dict.get("description", None),
                    )