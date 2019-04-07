import asyncio
import time
from discord import Reaction, User, Client
from discord.ext import commands
import discord
from discord.ext.commands import Bot
import json
from math import hypot, floor, modf
import legendutils
from discordgame import DiscordGame
import legend
from threading import Thread

# Bump Position ID for speeds
bump_colors = {}
bump_colors[(0, 0, 0)] = 0  # Solid Tile
bump_colors[(255, 255, 255)] = 1  # Transparent Tile
bump_colors[(255, 0, 0)] = 2  # Random Encounter Tile


def create_bot(config, legend_game: legend.Legend):
    legend_bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["prefix"]), description="Legend RPG Bot",
                              activity=discord.Game(name='Legend | +help'))

    class LegendBot(commands.Cog):

        def __init__(self, bot: Bot, config, legend: legend.Legend):
            print("Init LegendBot")
            with open("config/config.json") as f:
                self.config = json.load(f)
            self.w_screen: int = None
            self.h_screen: int = None

            self.config = config
            self.bot: Bot = bot
            self.legend = legend
            self.load_config()
            self.running = True
            self.legend.bot = self

            bot.loop.create_task(self.background())

        async def background(self):
            await self.bot.wait_until_ready()
            await self.legend.after_bot(self.bot.loop)
            await self.update()

        def load_config(self):
            self.w_screen = self.config["screen_width"]
            self.h_screen = self.config["screen_height"]

        def reload_config(self):
            self.load_config()

        @commands.command()
        async def ping(self, ctx):
            await ctx.send('Pong!')

        @commands.command()
        async def help(self, ctx):
            await ctx.send('TODO:')

        @commands.command()
        async def game(self, ctx):
            if ctx.author.id in self.legend.games:
                await self.legend.games[ctx.author.id].disconnect()
                self.legend.games.pop(ctx.author.id)
            self.legend.games[ctx.author.id] = DiscordGame(ctx, self.config, self.legend.users, self.legend.world,
                                                           self.legend.games, self.bot, self.legend.sprites,
                                                           self.legend.dialogue, self.legend.base_items)
            await self.legend.games[ctx.author.id].start()

        @commands.command()
        async def say(self, ctx, *, msg):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                await self.chat(ctx, msg, self.legend.games[ctx.author.id])
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def s(self, ctx, *, msg):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                await self.chat(ctx, msg, self.legend.games[ctx.author.id])
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def inventory(self, ctx, ):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                if self.legend.games[ctx.author.id].mode == "world":
                    await self.open_inventory(self.legend.games[ctx.author.id])
                else:
                    await ctx.send("You can only use this command from the overworld!")
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def i(self, ctx):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                if self.legend.games[ctx.author.id].mode == "world":
                    await self.open_inventory(self.legend.games[ctx.author.id])
                else:
                    await ctx.send("You can only use this command from the overworld!")
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def inv(self, ctx):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                if self.legend.games[ctx.author.id].mode == "world":
                    await self.open_inventory(self.legend.games[ctx.author.id])
                else:
                    await ctx.send("You can only use this command from the overworld!")
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def tp(self, ctx, x: int, y: int):
            if ctx.author.id in self.legend.games and self.legend.games[ctx.author.id].running:
                self.legend.games[ctx.author.id].move(x, y, force=True)
            else:
                await ctx.send("You can only use this command ingame!")

        @commands.command()
        async def stop(self, ctx):
            user_data = self.legend.users.find_one({"user": str(ctx.author.id)})
            if user_data and "admin" in user_data and user_data["admin"]:
                for k in list(self.legend.games.keys()):
                    await self.legend.games[k].disconnect("Bot is restarting, join back in a couple minutes")
                    self.legend.games.pop(k)
                print("Exiting")
                self.running = False
                await self.bot.close()
            else:
                await ctx.send("You do not have permissions!")

        @commands.command()
        async def reload(self, ctx):
            user_data = self.legend.users.find_one({"user": str(ctx.author.id)})
            if user_data and "admin" in user_data and user_data["admin"]:
                self.reload_config()
                await ctx.send("Config reloaded.")
            else:
                await ctx.send("You do not have permissions!")

        async def chat(self, ctx, msg, og):
            for g in self.legend.games:
                dist = hypot(self.legend.games[g].data["pos_x"] - og.data["pos_x"],
                             self.legend.games[g].data["pos_y"] - og.data["pos_y"])
                if dist <= self.legend.chat_radius:
                    self.legend.games[g].add_msg(legendutils.ChatMessage(ctx.author.name, ctx.author.discriminator,
                                                                         msg))

        async def open_inventory(self, og: DiscordGame):
            await og.open_inventory()

        @commands.Cog.listener(name='on_reaction_add')
        async def on_reaction_add(self, reaction: Reaction, user: User = None):
            if user and user.id in self.legend.games and self.legend.games[user.id].running:
                await self.legend.games[user.id].react(reaction)

        @commands.Cog.listener(name='on_reaction_remove')
        async def on_reaction_remove(self, reaction: Reaction, user: User = None):
            if user and user.id in self.legend.games and self.legend.games[user.id].running:
                await self.legend.games[user.id].react(reaction)

        async def update(self):
            offset = 0
            while self.running:
                timing = modf(time.time() / self.config["frequency"])
                if floor(timing[0] * 10) != offset:
                    # print("From " + str(offset) + " to " + str(floor(timing[0] * 10)) + " @ " + str(timing[1]))
                    offset = floor(timing[0] * 10)
                    removals = []
                    for user_id in self.legend.games:
                        if self.legend.games[user_id].offset == offset and self.legend.games[user_id].running:
                            session = self.legend.games[user_id]
                            cur_time = time.time()
                            if (cur_time - session.timeout) > self.config["timeout"]:
                                await session.disconnect("Inactivity")
                            else:
                                await session.frame()
                        elif not self.legend.games[user_id].running and self.legend.games[user_id].started:
                            removals.append(user_id)
                    for removal in removals:
                        del self.legend.games[removal]
                await asyncio.sleep(self.config["frequency"] / 20)

    legend_bot.remove_command("help")
    bot = LegendBot(legend_bot, config, legend_game)
    legend_bot.add_cog(bot)

    @legend_bot.event
    async def on_ready():
        print('Logged in as:\n{0} (ID: {0.id})'.format(legend_bot.user))

    print("Run Bot")
    legend_bot.run(config["token"])

    return bot
