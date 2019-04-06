from PIL import Image
from pymongo import MongoClient
import json
import numpy
from typing import Dict, Any, Tuple, List
import interactions
import items
import legendutils
import requirements
from battles import Battle
from discordgame import DiscordGame
from entities import Entity, NPC
from legendutils import World
from server import Server


class Legend:
    # Bump Position ID for speeds
    bump_colors = {}
    bump_colors[(0, 0, 0)] = 0  # Solid Tile
    bump_colors[(255, 255, 255)] = 1  # Transparent Tile
    bump_colors[(255, 0, 0)] = 2  # Random Encounter Tile

    def __init__(self, config):
        import bot
        self.config = config
        # Values from config
        self.sprites = {}
        self.colors: List[str] = []
        self.color_map: Dict[str, int] = {}
        self.bump_width: int = None
        self.bump_height: int = None
        self.width: int = None
        self.height: int = None
        self.chat_radius: int = None
        self.max_buffer: int = None
        self.world_map: numpy.ndarray = None
        self.bump_map: numpy.ndarray = None
        self.portals: Dict[Tuple[int, int], Dict[str, int]] = {}
        self.entities: Dict[Tuple[int, int], Entity] = {}
        self.dialogue: Dict[str, interactions.Dialogue] = {}
        self.base_items: Dict[str, dict] = {}
        self.messages = {}
        self.battles: List[Battle] = []

        self.config = config
        self.mongo = MongoClient()
        self.legend_db = self.mongo.legend
        self.users = self.legend_db.users
        self.games: Dict[str, DiscordGame] = {}
        self.load_config()
        self.world = World(self.world_map, self.bump_map, self.portals, self.entities)
        self.bot = bot.create_bot(config, self)
        self.server = Server(config)
        self.running = True

    def load_config(self):
        with open("config/" + self.config["sprites"]) as sprites_f:
            self.sprites = json.load(sprites_f)

        # Open the img in the world argument
        im = Image.open("config/" + self.config["world_map"])
        # Get image width and height for the world
        self.width, self.height = im.size

        self.chat_radius = self.config["chat_radius"]
        self.max_buffer = self.config["chat_buffer"]

        # World list
        self.world_map = []
        self.bump_map = []

        print("Loading " + self.config["world_map"] + " " + str(self.width) + " x " + str(self.height) + "\n")

        for y in range(self.height):
            # Loop over every line
            line = []
            for x in range(self.width):
                # Create a line variable for the x values, using their color index
                found_tile: bool = False
                pixel = legendutils.to_hex(im.getpixel((x, y)))
                for pt in range(len(self.sprites["tiles"])):
                    if self.sprites["tiles"][pt]["color"] == pixel:
                        line.append(pt)
                        found_tile = True
                if not found_tile:
                    line.append(0)
            # Add the line to the world
            # world[y][x]
            self.world_map.append(line)

        # Open the img in the bump argument
        im = Image.open("config/" + self.config["bump_map"])
        # Get image width and height for the world
        self.bump_width, self.bump_height = im.size
        if self.bump_width != self.width or self.bump_height != self.height:
            print("World/Bump Map MISMATCH!!!")
            exit()

        print("Loading " + self.config["bump_map"] + " " + str(self.bump_width) + " x " + str(
            self.bump_height) + "\n")

        for y in range(self.height):
            # Loop over every line
            line = []
            for x in range(self.width):
                # Create a line variable for the x values, using their color index
                line.append(self.bump_colors[im.getpixel((x, y))])
            # Add the line to the world
            # world[y][x]
            self.bump_map.append(line)

        print("Loading portals")
        with open("config/" + self.config["portals"]) as f:
            portal_json = json.load(f)

        self.portals.clear()

        for portal in portal_json:
            self.portals[(portal["pos_x"], portal["pos_y"])] = portal

        print("Loading base items")
        with open("config/" + self.config["items"]) as f:
            self.base_items = json.load(f)

        print("Loading dialogue")
        with open("config/" + self.config["dialogue"]) as f:
            dialogue_json = json.load(f)

        self.dialogue.clear()

        for dialogue_id in dialogue_json:
            dialogue = dialogue_json[dialogue_id]
            options = []
            for opt in dialogue["options"]:
                if opt["type"] == "end":
                    result = interactions.CloseGuiResult()
                elif opt["type"] == "dialogue":
                    result = interactions.ContinueDialogueResult(opt["dialogue"])
                else:
                    result = interactions.CloseGuiResult()
                reqs = None
                if "requirements" in opt:
                    reqs = [requirements.requirement_from_dict(req) for req in opt["requirements"]]
                options.append(interactions.DialogueOption(opt["text"], result, reqs))
            dialogue_items = None
            flags = None
            if "items" in dialogue:
                dialogue_items = [(items.from_dict(item["item"], self.base_items), item["give"]) for item in
                                  dialogue["items"]]
            if "flags" in dialogue:
                flags = [requirements.operation_from_dict(flag) for flag in dialogue["flags"]]
            self.dialogue[dialogue_id] = interactions.Dialogue(dialogue["author"], dialogue["text"],
                                                               dialogue["sprite"], options, dialogue_items, flags)

        print("Loading entities")
        with open("config/" + self.config["entities"]) as f:
            entity_json = json.load(f)

        self.entities.clear()

        for entity in entity_json:
            if entity["type"] == "npc":
                self.entities[(entity["pos_x"], entity["pos_y"])] = \
                    NPC(entity["pos_x"], entity["pos_y"], entity["tile"], self.dialogue[entity["dialogue"]])
        # Turn it into a numpy array for 2d calculations and speed.
        self.world_map = numpy.array(self.world_map)
        self.bump_map = numpy.array(self.bump_map)

    def reload_config(self):
        with open("config/config.json") as f:
            self.config = json.load(f)
        self.load_config()
        self.world.reload(self.world_map, self.bump_map, self.portals, self.entities)