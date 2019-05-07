import asyncio
import time
from typing import List, Dict

import discord
from discord import embeds

import items
import copy
from game import Game
from interactions import GuiOption, DialogueMessage, CloseGuiResult, ContinueDialogueResult, Dialogue
from inventory import Inventory
from legendutils import View, ChatMessage, World
import sprite_render
from math import ceil, floor, modf

from packets import InvalidateCachePacket

overworld_modes: List[str] = ["world", "dialogue"]
inventory_modes: List[str] = ["inventory", "inventory_context"]
context_count: int = 3
context_options: List[str] = ["Equip", "Drop", "Move"]


class DiscordGame(Game):

    def __init__(self, ctx, users, bot, legend):
        global inv_filters
        super().__init__(0, 0, legend, ctx.author.name + "#" + ctx.author.discriminator, ctx.author.id)
        self.error: str = ""
        self.gui_options: List[GuiOption] = []
        if isinstance(ctx.channel, discord.DMChannel):
            self.error = "This command cannot be ran from DMs!"
            return
        self.ctx = ctx
        self.users = users
        self.bot = bot
        self.chat_buffer: List[ChatMessage] = []
        self.dialogue_buffer: DialogueMessage = None
        self.last_dialogue: DialogueMessage = None
        self.gui_description: str = ""
        self.author: discord.user = ctx.author
        self.facings: List[str] = ["left", "up", "down", "right"]
        self.previous_render = ""
        self.previous_inv_render = ""
        self.last_msg = None
        self.msg = None
        self.mode: str = ""
        self.last_frame: int = 0
        self.context_cursor: int = 0
        self.confirm_drop: bool = False
        self.timeout = time.time()
        timing = modf(time.time() / self.legend.config["frequency"])
        self.offset = floor(timing[0] * 10)
        self.start_time = timing[1]

    def get_char_tile(self, view: View, vx: int, vy: int):
        return self.legend.sprites["tiles"][view.view[vy][vx]]["char"]

    def get_view(self, pos_x: int, pos_y: int):
        # Amount of height above, and below x respectively
        height_up = ceil(self.legend.config["screen_height"] / 2)
        height_down = floor(self.legend.config["screen_height"] / 2)
        # Amount of width to the left, and right of x respectively
        width_left = ceil(self.legend.config["screen_width"] / 2)
        width_right = ceil(self.legend.config["screen_width"] / 2)

        if pos_y + height_down > self.legend.world.height:
            # If the bottom of the screen would be below the world
            # Show from world height upwards
            max_y = self.legend.world.height
            min_y = max_y - self.legend.config["screen_height"]
        else:
            # Otherwise show roughly screen_height / 2 units below and above the player,
            # Limiting once again to be within the world from above
            min_y = max(0, pos_y - height_up)
            max_y = min_y + self.legend.config["screen_height"]

        if pos_x + width_right > self.legend.world.width:
            # If the right-most part of the screen would be outside the world
            # Show from the right edge leftwards
            max_x = self.legend.world.width
            min_x = max_x - self.legend.config["screen_width"]
        else:
            # Otherwise, make sure we're within the border from the left
            # And get max_x from that
            min_x = max(0, pos_x - width_left)
            max_x = min_x + self.legend.config["screen_width"]
        # Then get the array from our view
        world_section = self.legend.world.get(min_x, max_x, min_y, max_y)
        return View(world_section, min_x, max_x, min_y, max_y)

    def render_view(self, view: View):
        positions = {}
        for i in self.legend.games:
            g = self.legend.games[i]
            if g.user_id == self.user_id or not (g.data["pos_x"], g.data["pos_y"]) in positions:
                positions[(g.data["pos_x"], g.data["pos_y"])] = (g.user_id, g.facing)
        render = ""
        for vy in range(len(view.view)):
            render += "\n"
            for vx in range(len(view.view[vy])):
                abs_x = vx + view.min_x
                abs_y = vy + view.min_y
                if (abs_x, abs_y) in positions:
                    if positions[(abs_x, abs_y)] == (self.user_id, self.facing):
                        if not self.legend.world.collide(abs_x, abs_y):
                            render += self.legend.sprites["characters"][self.sprite]["player"][self.get_char_tile(view, vx, vy)][self.facings[self.facing]]
                        else:
                            render += self.legend.sprites["characters"][self.sprite]["player"][self.get_char_tile(view, vx, vy)][self.facings[self.facing]]
                    else:
                        # TODO: Replace sprites of other users based on their sprite
                        render += self.legend.sprites["characters"]["rowan"]["other"][self.get_char_tile(view, vx, vy)][self.facings[positions[(abs_x, abs_y)][1]]]
                elif self.legend.world.get_entity(abs_x, abs_y):
                    entity = self.legend.world.get_entity(abs_x, abs_y)
                    render += self.legend.sprites["entities"][entity.sprite + "_" + self.facings[entity.facing]]
                else:
                    render += self.legend.sprites["tiles"][view.view[vy][vx]]["emoji"]
        return render[1:]

    async def update_screen(self, render: str, inv_render: str = None):
        if render != self.previous_render or (len(self.chat_buffer) > 0
                                              and self.last_msg != self.chat_buffer[-1].message) \
                or self.dialogue_buffer != self.last_dialogue \
                or self.previous_inv_render != self.opened_inventory.get_filter():
            embed = embeds.Embed(
                color=10038562,
                title="Legend",
                url="https://discordapp.com",
                description=render
            )
            self.previous_render = render
            if self.dialogue_buffer:
                self.last_dialogue = self.dialogue_buffer
                author_text = self.legend.sprites["entities"][self.dialogue_buffer.sprite] + self.dialogue_buffer.author
                message = self.dialogue_buffer.text
                embed.add_field(name=author_text, value=message, inline=False)
                #  if not self.gui_description or self.gui_description == "":
                #    self.gui_description = "."
                embed.add_field(name="Choose", value=self.gui_description, inline=False)

            if len(self.chat_buffer) > 0:
                self.last_msg = self.chat_buffer[-1]
                for chat_msg in self.chat_buffer:
                    s_time = chat_msg.time.strftime("%H:%M:%S")
                    author_text = chat_msg.author + " - " + s_time
                    embed.add_field(name=author_text, value=chat_msg.message, inline=False)

            if inv_render:
                bag_desc: str = "Bag " + str(min(self.opened_inventory.cursor + 1, len(self.opened_inventory.view))) +\
                                "/" + str(len(self.opened_inventory.view))
                self.previous_inv_render = bag_desc + "\n" + inv_render
                embed.add_field(name=bag_desc, value=inv_render, inline=False)
                equipment_desc = "Equipment"

                equipment_render = self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["gui"]["equipment_head"]
                equipment_render += self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["gui"]["stats_max_health"] + " "
                equipment_render += sprite_render.render_integer(self.legend.sprites, 420, 3)
                equipment_render += "\n"

                equipment_render += self.legend.sprites["gui"]["equipment_offhand"]
                equipment_render += self.legend.sprites["gui"]["equipment_body"]
                equipment_render += self.legend.sprites["gui"]["equipment_hand"]
                equipment_render += self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["gui"]["stats_armor"] + " "
                equipment_render += sprite_render.render_integer(self.legend.sprites, 69, 3)
                equipment_render += "\n"

                equipment_render += self.legend.sprites["gui"]["equipment_special"]
                equipment_render += self.legend.sprites["gui"]["equipment_legs"]
                equipment_render += self.legend.sprites["gui"]["equipment_special"]
                equipment_render += self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["gui"]["stats_sword"] + " "
                equipment_render += sprite_render.render_integer(self.legend.sprites, 0, 3)
                equipment_render += "\n"

                equipment_render += self.legend.sprites["utility"]["spacing"]
                equipment_render += self.legend.sprites["gui"]["equipment_feet"]
                equipment_render += (self.legend.sprites["utility"]["spacing"] * 2)
                equipment_render += self.legend.sprites["gui"]["stats_shield"] + " "
                equipment_render += sprite_render.render_integer(self.legend.sprites, 999, 3)
                equipment_render += "\n"
                embed.add_field(name=equipment_desc, value=equipment_render, inline=False)

            await self.msg.edit(embed=embed)
            self.last_frame = time.time()

    def render_items(self, inv: Inventory) -> str:
        global context_options
        cursor_pos: int = inv.cursor
        screen_pos: int = inv.screen_cursor
        output: str = ""
        if screen_pos > 0:
            output += "⏫ "
        else:
            output += self.legend.sprites["utility"]["spacing"] + " "
        output += (self.legend.sprites["utility"]["spacing"] + " ") * 2
        output += "◀ " + self.opened_inventory.get_filter() + " ▶\n"
        for x in range(len(inv.inv_display)):
            if (x+screen_pos) != cursor_pos:
                output += self.legend.sprites["utility"]["spacing"] + " "
            else:
                if self.mode == "inventory":
                    output += "▶ "
                else:
                    output += "⤵ "
            output += self.legend.sprites["items"][inv.inv_display[x].get_sprite(self.legend.base_items)] + " " +\
                inv.inv_display[x].get_name(self.legend.base_items) + "\n"
            if self.mode == "inventory_context" and (x+screen_pos) == cursor_pos:
                for y in range(3):
                    output += self.legend.sprites["utility"]["spacing"] + " "
                    if self.context_cursor == y:
                        output += "▶" + " "
                    else:
                        output += self.legend.sprites["utility"]["spacing"] + " "
                    output += context_options[y]
                    if context_options[y] == "Drop" and self.confirm_drop:
                        output += " **[Confirm]**"
                    output += "\n"
        if (screen_pos + self.legend.config["items_per_page"]) < (len(inv.view)):
            output += "⏬"
        else:
            output += self.legend.sprites["utility"]["spacing"]
        return output

    def render_item_info(self, item: items.Item) -> str:
        output: str = ""
        output += self.legend.sprites["items"][item.get_sprite(self.legend.base_items)] + "\n"
        if isinstance(item, items.Weapon):
            output += "**Name:** " + self.legend.sprites["items"][item.get_weapon_class(self.legend.base_items)] + " " +\
                      item.get_name(self.legend.base_items) + "\n"
        else:
            output += "**Name:** " + self.legend.sprites["items"][item.get_item_type(self.legend.base_items)] + " " +\
                      item.get_name(self.legend.base_items) + "\n"
        output += "**Description:** " + item.get_description(self.legend.base_items) + "\n"
        if isinstance(item, items.Weapon):
            output += "**Damage:** " + str(item.get_damage(self.legend.base_items))
        return output

    async def frame(self):
        global overworld_modes
        global inventory_modes
        if self.mode in overworld_modes:
            view = self.get_view(self.data["pos_x"], self.data["pos_y"])
            render = self.render_view(view)
            await self.update_screen(render)
        elif self.mode in inventory_modes:
            inv_render = self.render_items(self.opened_inventory)
            if self.opened_inventory.cursor < len(self.opened_inventory.view):
                item_render = self.render_item_info(self.opened_inventory.view[self.opened_inventory.cursor])
            else:
                item_render = ""
            # print(str(inv_render))
            await self.update_screen(item_render, inv_render=inv_render)
        return

    async def optional_frame(self) -> None:
        if (time.time() - self.legend.config["frequency"]) > self.last_frame:
            # It's been awhile since the last frame, we can just go ahead and do one now.
            await self.frame()

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
                new_dialogue = self.legend.dialogue[selected_result.dialogue_id]
                new_dialogue.interact(self)

    def add_msg(self, message: ChatMessage, x, y) -> None:
        self.chat_buffer.append(message)
        if len(self.chat_buffer) > self.legend.config["chat_buffer"]:
            self.chat_buffer.pop(0)

    async def start(self):
        if self.error and self.error != "":
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
            for arrow in self.legend.config["arrows"]:
                await self.msg.add_reaction(arrow)
            self.running = True
            self.started = True
            self.mode = "world"

    async def open_inventory(self, inventory: List[items.Item] = None):
        global inv_filters
        if inventory is None:
            self.opened_inventory = self.player_inventory
        else:
            self.opened_inventory = inventory
        self.mode = "inventory"
        self.opened_inventory.cursor = 0
        self.opened_inventory.screen_cursor = 0
        self.opened_inventory.filter_index = 0
        self.opened_inventory.set_filter(self.opened_inventory.get_filter())
        await self.optional_frame()

    async def react(self, reaction):
        global inv_filters
        global context_count
        if self.running:
            self.timeout = time.time()
            emoji = reaction.emoji
            if self.mode == "world":
                if emoji == self.legend.config["arrows"][0]:  # Left
                    self.facing = 0
                    self.move(self.data["pos_x"] - 1, self.data["pos_y"])
                elif emoji == self.legend.config["arrows"][1]:  # Up
                    self.facing = 1
                    self.move(self.data["pos_x"], self.data["pos_y"] - 1)
                elif emoji == self.legend.config["arrows"][2]:  # Down
                    self.facing = 2
                    self.move(self.data["pos_x"], self.data["pos_y"] + 1)
                elif emoji == self.legend.config["arrows"][3]:  # Right
                    self.facing = 3
                    self.move(self.data["pos_x"] + 1, self.data["pos_y"])
                elif emoji == self.legend.config["arrows"][4]:  # X
                    pass
                elif emoji == self.legend.config["arrows"][5]:  # Confirm
                    pass
            elif self.mode == "dialogue":
                self.gui_interact(self.legend.config["arrows"].index(emoji))
            elif self.mode == "inventory":
                if emoji == self.legend.config["arrows"][0]:  # Left
                    self.opened_inventory.prev_filter()
                elif emoji == self.legend.config["arrows"][3]:  # Right
                    self.opened_inventory.next_filter()
                elif emoji == self.legend.config["arrows"][2]:  # Down
                    self.opened_inventory.cursor_down()
                elif emoji == self.legend.config["arrows"][1]:  # Up
                    self.opened_inventory.cursor_up()
                elif emoji == self.legend.config["arrows"][4]:  # X
                    self.mode = "world"
                    self.opened_inventory = Inventory([], self.legend.base_items, self.legend.config)
                elif emoji == self.legend.config["arrows"][5]:  # Confirm
                    if self.opened_inventory.cursor < len(self.opened_inventory.view):
                        self.confirm_drop = False
                        self.mode = "inventory_context"
                        self.context_cursor = 0
            elif self.mode == "inventory_context":
                if emoji == self.legend.config["arrows"][1]:  # Up
                    self.confirm_drop = False
                    if self.context_cursor > 0:
                        self.context_cursor -= 1
                    else:
                        self.context_cursor = (context_count - 1)
                elif emoji == self.legend.config["arrows"][2]:  # Down
                    self.confirm_drop = False
                    if self.context_cursor < (context_count - 1):
                        self.context_cursor += 1
                    else:
                        self.context_cursor = 0
                elif emoji == self.legend.config["arrows"][4]:  # X
                    self.mode = "inventory"
                elif emoji == self.legend.config["arrows"][5]:  # Confirm
                    chosen_option = context_options[self.context_cursor]
                    if chosen_option == "Equip":
                        pass
                    elif chosen_option == "Drop":
                        if self.confirm_drop:
                            highlighted_item: items.Item = self.opened_inventory.view[self.opened_inventory.cursor]
                            self.opened_inventory.remove_item(highlighted_item)
                            self.confirm_drop = False
                            self.mode = "inventory"
                            self.opened_inventory.cursor_up()
                        else:
                            self.confirm_drop = True
                    elif chosen_option == "Move":
                        pass
                    else:
                        pass
            await self.optional_frame()

    async def disconnect(self, reason=None):
        if self.running:
            from directgame import DirectGame
            self.running = False
            for game in self.legend.games.values():
                if isinstance(game, DirectGame) and self.uuid in game.entity_cache:
                    invalidate_cache_packet = InvalidateCachePacket(self.uuid)
                    game.connection.send_packet(invalidate_cache_packet)
                    game.entity_cache.remove(self.uuid)
            self.data["inventory"] = [vars(inv_item) for inv_item in self.data["inventory"].items]
            self.users.update_one({"user": str(self.author.id)}, {"$set": self.data})
            if not reason:
                await self.msg.edit(content="❌ Disconnected", embed=None)
            else:
                await self.msg.edit(content="❌ Disconnected for " + reason, embed=None)
            return self.author
        else:
            return False
