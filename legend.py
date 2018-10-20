import asyncio
from typing import Dict, Any

from discord.ext import commands
import discord
import json

import legendutils
from legendgame import LegendGame
from legendutils import World
from legendutils import ChatMessage
from math import hypot
from pymongo import MongoClient
import numpy
from PIL import Image

with open("config.json") as f:
    config = json.load(f)

legend_bot = commands.Bot(command_prefix=config["prefix"], description="Legend RPG Bot",
                          activity=discord.Game(name='Legend | +help'))

# Bump Position ID for speeds
bump_colors = {}
bump_colors[(0, 0, 0)] = 0
bump_colors[(255, 255, 255)] = 1


class LegendBot:

    def __init__(self, bot):
        global config
        self.config = config
        self.bot = bot

        with open(self.config["sprites"]) as sprites_f:
            self.sprites = json.load(sprites_f)

        # Open the img in the world argument
        im = Image.open(self.config["world_map"])
        # Get image width and height for the world
        self.width, self.height = im.size

        # CONFIG: Screen width and height
        self.w_screen = self.config["screen_width"]
        self.h_screen = self.config["screen_height"]
        self.chat_radius = self.config["chat_radius"]
        self.max_buffer = self.config["chat_buffer"]

        # World list
        self.world_map = []
        self.bump_map = []
        self.messages = {}

        print("Loading " + self.config["world_map"] + " " + str(self.width) + " x " + str(self.height) + "\n")

        for y in range(self.height):
            # Loop over every line
            line = []
            for x in range(self.width):
                # Create a line variable for the x values, using their color index
                line.append(self.sprites["colors"][legendutils.to_hex(im.getpixel((x, y)))])
            # Add the line to the world
            # world[y][x]
            self.world_map.append(line)

        # Open the img in the bump argument
        im = Image.open(self.config["bump_map"])
        # Get image width and height for the world
        self.bump_width, self.bump_height = im.size
        if self.bump_width != self.width or self.bump_height != self.height:
            print("World/Bump Map MISMATCH!!!")
            exit()

        print("Loading " + self.config["bump_map"] + " " + str(self.bump_width) + " x " + str(self.bump_height) + "\n")

        for y in range(self.height):
            # Loop over every line
            line = []
            for x in range(self.width):
                # Create a line variable for the x values, using their color index
                line.append(bump_colors[im.getpixel((x, y))])
            # Add the line to the world
            # world[y][x]
            self.bump_map.append(line)

        print("Loading portals")
        with open(self.config["portals"]) as f:
            portal_json = json.load(f)

        portals = {}

        for portal in portal_json:
            portals[(portal["pos_x"], portal["pos_y"])] = portal
        # Turn it into a numpy array for 2d calculations and speed.
        self.world_map = numpy.array(self.world_map)
        self.bump_map = numpy.array(self.bump_map)
        self.portals = portals
        self.world = World(self.world_map, self.bump_map, self.portals)
        self.games = {} # type: Dict[str, LegendGame]
        self.mongo = MongoClient()
        self.legend_db = self.mongo.legend
        self.users = self.legend_db.users

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def help(self, ctx):
        await ctx.send('TODO:')

    @commands.command()
    async def game(self, ctx):
        if ctx.author.id in self.games:
            await self.games[ctx.author.id].disconnect()
            self.games.pop(ctx.author.id)
        self.games[ctx.author.id] = LegendGame(ctx, self.config, self.users, self.world, self.games, self.bot, self.sprites)
        await self.games[ctx.author.id].start()

    @commands.command()
    async def say(self, ctx, *, msg):
        if ctx.author.id in self.games and self.games[ctx.author.id].running:
            await self.chat(ctx, msg, self.games[ctx.author.id])
        else:
            await ctx.send("You can only use this command ingame!")

    @commands.command()
    async def s(self, ctx, *, msg):
        if ctx.author.id in self.games and self.games[ctx.author.id].running:
            await self.chat(ctx, msg, self.games[ctx.author.id])
        else:
            await ctx.send("You can only use this command ingame!")

    @commands.command()
    async def tp(self, ctx, x: int, y: int):
        if ctx.author.id in self.games and self.games[ctx.author.id].running:
            self.games[ctx.author.id].move(x, y, force=True)
        else:
            await ctx.send("You can only use this command ingame!")

    @commands.command()
    async def stop(self, ctx):
        user_data = self.users.find_one({"user": str(ctx.author.id)})
        if user_data and "admin" in user_data and user_data["admin"]:
            for k in list(self.games.keys()):
                await self.games[k].disconnect("Bot is restarting, join back in a couple minutes")
                self.games.pop(k)
            print("Exiting")
            await self.bot.close()
        else:
            await ctx.send("You do not have permissions!")

    async def chat(self, ctx, msg, og):
        for g in self.games:
            dist = hypot(self.games[g].data["pos_x"] - og.data["pos_x"], self.games[g].data["pos_y"] - og.data["pos_y"])
            if dist <= self.chat_radius:
                self.games[g].add_msg(ChatMessage(ctx.author.name, ctx.author.discriminator, msg))


legend_bot.remove_command("help")
legend_bot.add_cog(LegendBot(legend_bot))


@legend_bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(legend_bot.user))


legend_bot.run(config["token"])
