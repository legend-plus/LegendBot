import asyncio
import time
from typing import List, Dict

import discord
from discord import embeds

import items
from game import Game
from interactions import GuiOption, DialogueMessage, CloseGuiResult, ContinueDialogueResult, Dialogue
from legendutils import View, ChatMessage, World
from math import ceil, floor, modf


class LegendGame(Game):

    def __init__(self, ctx, config, users, world, games, bot, sprites, dialogue, base_items):
        super().__init__(0, 0)
        self.ready: bool = False
        self.running: bool = False
        self.started: bool = False
        self.error: str = ""
        self.gui_options: List[GuiOption] = []
        if isinstance(ctx.channel, discord.DMChannel):
            self.error = "This command cannot be ran from DMs!"
            return
        user_data = users.find_one({"user": str(ctx.author.id)})
        if not user_data:
            user_data = config["default_user"]
            user_data["user"] = ctx.author.id
            users.insert_one(user_data)
        self.config = config
        self.ctx = ctx
        self.users = users
        self.world: World = world
        self.bot = bot
        self.sprites = sprites
        self.dialogue: Dict[str, Dialogue] = dialogue
        self.base_items: Dict[str, dict] = base_items
        self.chat_buffer: List[ChatMessage] = []
        self.dialogue_buffer: DialogueMessage = None
        self.last_dialogue: DialogueMessage = None
        self.gui_description: str = ""
        self.games = games
        self.author: discord.user = ctx.author
        self.data = user_data
        inv = [items.from_dict(inv_item, base_items) for inv_item in self.data["inventory"]]
        self.data["inventory"] = inv
        self.previous_render = ""
        self.last_msg = None
        self.msg = None
        self.mode: str = ""
        self.last_frame: int = 0
        self.timeout = time.time()
        timing = modf(time.time() / self.config["frequency"])
        self.offset = floor(timing[0] * 10)
        self.start_time = timing[1]

    def get_view(self, pos_x: int, pos_y: int):
        # Amount of height above, and below x respectively
        height_up = ceil(self.config["screen_height"] / 2)
        height_down = floor(self.config["screen_height"] / 2)
        # Amount of width to the left, and right of x respectively
        width_left = ceil(self.config["screen_width"] / 2)
        width_right = ceil(self.config["screen_width"] / 2)

        if pos_y + height_down > self.world.height:
            # If the bottom of the screen would be below the world
            # Show from world height upwards
            max_y = self.world.height
            min_y = max_y - self.config["screen_height"]
        else:
            # Otherwise show roughly screen_height / 2 units below and above the player,
            # Limiting once again to be within the world from above
            min_y = max(0, pos_y - height_up)
            max_y = min_y + self.config["screen_height"]

        if pos_x + width_right > self.world.width:
            # If the right-most part of the screen would be outside the world
            # Show from the right edge leftwards
            max_x = self.world.width
            min_x = max_x - self.config["screen_width"]
        else:
            # Otherwise, make sure we're within the border from the left
            # And get max_x from that
            min_x = max(0, pos_x - width_left)
            max_x = min_x + self.config["screen_width"]
        # Then get the array from our view
        world_section = self.world.get(min_x, max_x, min_y, max_y)
        return View(world_section, min_x, max_x, min_y, max_y)

    def render_view(self, view: View):
        positions = {}
        for i in self.games:
            g = self.games[i]
            if g.author == self.author or not (g.data["pos_x"], g.data["pos_y"]) in positions:
                positions[(g.data["pos_x"], g.data["pos_y"])] = g.author
        render = ""
        for vy in range(len(view.view)):
            render += "\n"
            for vx in range(len(view.view[vy])):
                abs_x = vx + view.min_x
                abs_y = vy + view.min_y
                if (abs_x, abs_y) in positions:
                    if positions[(abs_x, abs_y)] == self.author:
                        if not self.world.collide(abs_x, abs_y):
                            render += self.sprites["character_one_pc"][view.view[vy][vx]]["emoji"]
                        else:
                            render += self.sprites["character_one_pc"][34]["emoji"]
                    else:
                        render += self.sprites["character_one"][view.view[vy][vx]]["emoji"]
                elif self.world.get_entity(abs_x, abs_y):
                    entity = self.world.get_entity(abs_x, abs_y)
                    render += self.sprites["entities"][entity.tile]
                else:
                    render += self.sprites["tiles"][view.view[vy][vx]]["emoji"]
        return render[1:]

    async def update_screen(self, render: str):
        if render != self.previous_render or (len(self.chat_buffer) > 0
                                              and self.last_msg != self.chat_buffer[-1].message) \
                or self.dialogue_buffer != self.last_dialogue:
            embed = embeds.Embed(
                color=10038562,
                title="Legend",
                url="https://discordapp.com",
                description=render
            )

            self.previous_render = render
            if self.dialogue_buffer:
                self.last_dialogue = self.dialogue_buffer
                author_text = self.sprites["entities"][self.dialogue_buffer.sprite] + self.dialogue_buffer.author
                message = self.dialogue_buffer.text
                embed.add_field(name=author_text, value=message, inline=False)
                embed.add_field(name="Choose", value=self.gui_description, inline=False)

            if len(self.chat_buffer) > 0:
                self.last_msg = self.chat_buffer[-1]
                for chat_msg in self.chat_buffer:
                    s_time = chat_msg.time.strftime("%H:%M:%S")
                    author_text = chat_msg.author + "#" + chat_msg.discriminator + " - " + s_time
                    embed.add_field(name=author_text, value=chat_msg.message, inline=False)
            await self.msg.edit(embed=embed)
            self.last_frame = time.time()

    async def frame(self):
        view = self.get_view(self.data["pos_x"], self.data["pos_y"])
        render = self.render_view(view)
        await self.update_screen(render)
        return

    async def optional_frame(self) -> None:
        if (time.time() - self.config["frequency"]) > self.last_frame:
            # It's been awhile since the last frame, we can just go ahead and do one now.
            await self.frame()

    def move(self, x: int, y: int, force: bool = False) -> bool:
        if self.running and self.world.height > y >= 0 and self.world.width > x >= 0:
            if force or not self.world.collide(x, y):
                if self.world.get_portal(x, y):
                    destination_portal = self.world.get_portal(x, y)
                    self.data["pos_x"] = destination_portal["to_x"]
                    self.data["pos_y"] = destination_portal["to_y"]
                else:
                    if self.world.can_trigger_encounters(x, y):
                        self.data["pos_x"] = x
                        self.data["pos_y"] = y
                        pass  # encounter =
                    else:
                        self.data["pos_x"] = x
                        self.data["pos_y"] = y
                return True
            else:
                if self.world.get_entity(x, y):
                    entity = self.world.get_entity(x, y)
                    if entity.interactable:
                        entity.interact(self)
                return False
        else:
            return False

    def gui_interact(self, choice: int):
        if self.gui_options and len(self.gui_options) > choice:
            selected_choice = self.gui_options[choice]
            selected_result = selected_choice.result
            # TODO: Rewards
            if isinstance(selected_result, CloseGuiResult):
                self.mode = "world"
                self.dialogue_buffer = None
                self.gui_description = ""
                self.gui_options = []
            elif isinstance(selected_result, ContinueDialogueResult):
                self.gui_options = []
                self.gui_description = ""
                self.dialogue_buffer = None
                new_dialogue = self.dialogue[selected_result.dialogue_id]
                new_dialogue.interact(self)

    def add_msg(self, message: ChatMessage) -> None:
        self.chat_buffer.append(message)
        if len(self.chat_buffer) > self.config["chat_buffer"]:
            self.chat_buffer.pop(0)

    async def start(self):
        if not self.ready and self.error:
            self.ctx.send(self.error)
        if not self.running:
            view = self.get_view(self.data["pos_x"], self.data["pos_y"])
            render = self.render_view(view)
            embed = embeds.Embed(
                color=10038562,
                title="Legend",
                url="https://discordapp.com",
                description=render
            )
            self.msg = await self.ctx.send(embed=embed)
            for arrow in self.config["arrows"]:
                await self.msg.add_reaction(arrow)
            self.running = True
            self.started = True
            self.mode = "world"

    async def react(self, reaction):
        if self.running:
            self.timeout = time.time()
            emoji = reaction.emoji
            if self.mode == "world":
                if emoji == self.config["arrows"][0]:
                    # Left
                    self.move(self.data["pos_x"] - 1, self.data["pos_y"])
                elif emoji == self.config["arrows"][1]:
                    # Up
                    self.move(self.data["pos_x"], self.data["pos_y"] - 1)
                elif emoji == self.config["arrows"][2]:
                    # Down
                    self.move(self.data["pos_x"], self.data["pos_y"] + 1)
                elif emoji == self.config["arrows"][3]:
                    # Right
                    self.move(self.data["pos_x"] + 1, self.data["pos_y"])
                elif emoji == self.config["arrows"][4]:
                    # Info
                    pass
                elif emoji == self.config["arrows"][5]:
                    # Confirm
                    pass
            elif self.mode == "dialogue":
                self.gui_interact(self.config["arrows"].index(emoji))
            await self.optional_frame()

    async def disconnect(self, reason=None):
        if self.running:
            self.data["inventory"] = [vars(inv_item) for inv_item in self.data["inventory"]]
            self.users.update_one({"user": str(self.author.id)}, {"$set": self.data})
            if not reason:
                await self.msg.edit(content="❌ Disconnected", embed=None)
            else:
                await self.msg.edit(content="❌ Disconnected for " + reason, embed=None)
            self.running = False
            return self.author
        else:
            return False
