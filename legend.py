import asyncio
from datetime import datetime
from discord.ext import commands
import discord
from discord import embeds
import json
from math import ceil, floor, hypot
from pymongo import MongoClient
import numpy
import sys
import time
from PIL import Image
import uuid

with open("config.json") as f:
	config = json.load(f)

bot = commands.Bot(command_prefix=config["prefix"], description="Legend RPG Bot", activity=discord.Game(name='Legend | +help'))


emoji_name = ":_:"
ep = ":_:" # Emoji prefix, save space with :_:

#Bump Position ID for speeds
bump_colors = {}
bump_colors[(0,0,0)] = 0
bump_colors[(255,255,255)] = 1

#Color index array for speed and easibility
#Equates to color_emoji
colors = {}
colors[(0,0,0)] = 0
colors[(34,32,52)] = 1
colors[(69,40,60)] = 2
colors[(102,57,49)] = 3
colors[(143,86,59)] = 4
colors[(223,113,38)] = 5
colors[(217,160,102)] = 6
colors[(238,195,154)] = 7
colors[(251,242,54)] = 8
colors[(153,229,80)] = 9
colors[(106,190,48)] = 10
colors[(55,148,110)] = 11
colors[(75,105,47)] = 12
colors[(82,75,36)] = 13
colors[(50,60,57)] = 14
colors[(63,63,116)] = 15
colors[(48,96,130)] = 16
colors[(91,110,225)] = 17
colors[(99,155,255)] = 18
colors[(95,205,228)] = 19
colors[(203,219,252)] = 20
colors[(255,255,255)] = 21
colors[(155,173,183)] = 22
colors[(132,126,135)] = 23
colors[(105,106,106)] = 24
colors[(89,86,82)] = 25
colors[(118,66,138)] = 26
colors[(172,50,50)] = 27
colors[(217,87,99)] = 28
colors[(215,123,186)] = 29
colors[(143,151,74)] = 30
colors[(138,111,48)] = 31

#List of emoji id's for the various colors
color_emoji = [];
color_emoji.append("498946323060490271") #Black
color_emoji.append("498946323396165652") #Valhalla
color_emoji.append("498946323609812992") #Loulou
color_emoji.append("498946323559481345") #Oiled Cedar
color_emoji.append("498946323597230081") #Rope
color_emoji.append("498946323408486421") #Tahiti Gold
color_emoji.append("498946322984992779") #Twine
color_emoji.append("498946323664338955") #Pancho
color_emoji.append("498946323719127040") #Golden Fizz
color_emoji.append("498946323458949136") #Atlantis
color_emoji.append("498946323572326400") #Christi
color_emoji.append("498946323752681492") #Elf Green
color_emoji.append("498946323471400972") #Dell
color_emoji.append("498946323018678284") #Verdigris
color_emoji.append("498946323714801664") #Opal
color_emoji.append("498946323542704178") #Deep Koamaru
color_emoji.append("498946323387777024") #Venice Blue
color_emoji.append("498946323291176967") #Royal Blue
color_emoji.append("498946323458818098") #Cornflower
color_emoji.append("498946323156959233") #Viking
color_emoji.append("498946323446235158") #Light Steel Blue
color_emoji.append("498946323211354125") #White
color_emoji.append("498946323353960472") #Heather
color_emoji.append("498946323446366208") #Topaz
color_emoji.append("498946323324862465") #Dim Gray
color_emoji.append("498946323479789570") #Smokey Ash
color_emoji.append("498946323412811801") #Clairvoyant
color_emoji.append("498946323219873793") #Brown
color_emoji.append("498946323731709959") #Mandy
color_emoji.append("498946323672727572") #Plum
color_emoji.append("498946323731447828") #Rain Forest
color_emoji.append("498946323291176967") #Stinger

sprites = {
"sans": [
	"<:_:499383523485155358>",
	"<a:_:499385501367664677>",
	"<:_:499383523677831168>",
	"<:_:499383523715710976>",
	"<a:_:499385501967450113>",
	"<a:_:499385501720117248>",
	"<a:_:499385501594419201>",
	"<a:_:499384574984585265>",
	"<:_:499383523619373056>",
	"<:_:499383523191554075>",
	"<:_:499383523749396491>",
	"<:_:499383523648471040>",
	"<:_:499383523543613440>",
	"<a:_:499385501556670464>",
	"<:_:499383523845603338>",
	"<:_:499383523636019200>",
	"<a:_:499385501569253424>",
	"<a:_:499385501799940096>",
	"<:_:499383523246080011>",
	"<a:_:499432338485280788>",
	"<:_:499383523627499520>",
	"<a:_:499385501652877313>",
	"<:_:499383523636150272>",
	"<a:_:499385501418258433>",
	"<:_:499383523392749569>",
	"<a:_:499385501715791872>",
	"<:_:499383523484893184>",
	"<:_:499383523531292718>",
	"<:_:499383523715710986>",
	"<a:_:499385501636231189>",
	"<a:_:499385501900341258>",
	"<a:_:499385501468590091>",
	"<a:_:499457501536976896>"
],
"sanspc": [
	"<a:_:499435126908780554>",
	"<a:_:499435127315628033>",
	"<a:_:499435126892265485>",
	"<a:_:499435127211032576>",
	"<a:_:499435127009705985>",
	"<a:_:499435127374479360>",
	"<a:_:499435127471079434>",
	"<a:_:499435127282073600>",
	"<a:_:499435126707453955>",
	"<a:_:499435126829088793>",
	"<a:_:499435126829219850>",
	"<a:_:499435126648864780>",
	"<a:_:499435126950854666>",
	"<a:_:499436185933053972>",
	"<a:_:499435127210770432>",
	"<a:_:499435126707716097>",
	"<a:_:499436185802768394>",
	"<a:_:499435127013638145>",
	"<a:_:499435126904848386>",
	"<a:_:499435127584194576>",
	"<a:_:499435127085072398>",
	"<a:_:499435127441719297>",
	"<a:_:499435126904717331>",
	"<a:_:499435127441588224>",
	"<a:_:499435126963437568>",
	"<a:_:499435127185866754>",
	"<a:_:499435126883614730>",
	"<a:_:499435126841671681>",
	"<a:_:499435127198187530>",
	"<a:_:499435127152312331>",
	"<a:_:499435127261233152>",
	"<a:_:499435127085072401>",
	"<a:_:499457501536976896>",
]
}

#view = get_view(10,10)
#print(render_view(10,10,view))

class ChatMessage:
	def __init__(self, author, discriminator, message):
		self.author = author
		self.discriminator = discriminator
		self.message = message[0:140]
		self.time = datetime.utcnow()
		self.uuid = uuid.uuid4().hex
	def __eq__(self, other):
		if isinstance(other, ChatMessage) and other.uuid == self.uuid:
			return True
		else:
			return False
	def __ne__(self, other):
		return not self.__eq__(other)
class View:
	def __init__(self, view, min_x, max_x, min_y, max_y):
		self.view = view
		self.min_x = min_x
		self.max_x = max_x
		self.min_y = min_y
		self.max_y = max_y

class World:
	def __init__(self, world, bump_map):
		self.height = len(world)
		self.width = len(world[0])
		self.world = world
		self.bump_map = bump_map
	def get(self, min_x, max_x, min_y, max_y):
		return self.world[min_y:max_y,min_x:max_x]
	def get_bump_map(self, min_x, max_x, min_y, max_y):
		return self.bump_map[min_y:max_y,min_x:max_x]
	def collide(self, pos_x, pos_y):
		return not self.bump_map[pos_y,pos_x]

class LegendGame:
	def __init__(self, ctx, config, users, world, games, bot):
		self.ready = False
		self.error = ""
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
		self.world = world
		self.bot = bot
		self.chat_buffer = []
		self.games = games
		self.author = ctx.author
		self.data = user_data
		self.previous_render = ""
		self.last_msg = None
	
	def get_view(self, pos_x, pos_y):
		#Amount of height above, and below x respectively
		height_up = ceil(self.config["screen_height"] / 2)
		height_down = floor(self.config["screen_height"] / 2)
		#Amount of width to the left, and right of x respectively
		width_left = ceil(self.config["screen_width"] / 2)
		width_right = ceil(self.config["screen_width"] / 2)
		
		if pos_y + height_down > self.world.height:
			#If the bottom of the screen would be below the world
			#Show from world height upwards
			max_y = self.world.height
			min_y = max_y - self.config["screen_height"]
		else:
			#Otherwise show roughly screen_height / 2 units below and above the player,
			#Limiting once again to be within the world from above
			min_y = max(0, pos_y - height_up)
			max_y = min_y + self.config["screen_height"]
		
		if pos_x + width_right > self.world.width:
			#If the right-most part of the screen would be outside the world
			#Show from the right edge leftwards
			max_x = self.world.width
			min_x = max_x - self.config["screen_width"]
		else:
			#Otherwise, make sure we're within the border from the left
			#And get max_x from that
			min_x = max(0, pos_x - width_left)
			max_x = min_x + self.config["screen_width"]
		#Then get the array from our view
		world_section = self.world.get(min_x,max_x,min_y,max_y)
		return View(world_section, min_x, max_x, min_y, max_y)
	
	def render_view(self, view):
		positions = {}
		for i in self.games:
			g = self.games[i]
			if g.author == self.author or not (g.data["pos_x"], g.data["pos_y"]) in positions:
				positions[(g.data["pos_x"], g.data["pos_y"])] = g.author
		render = ""
		for vy in range(len(view.view)):
			render += "\n"
			for vx in range(len(view.view[vy])):
				if (vx + view.min_x, vy + view.min_y) in positions:
					if positions[(vx + view.min_x, vy + view.min_y)] == self.author:
						if not self.world.collide(vx + view.min_x, vy + view.min_y):
							render += sprites["sanspc"][view.view[vy][vx]]
						else:
							render += sprites["sanspc"][32]
					else:
						render += sprites["sans"][view.view[vy][vx]]
				else:
					render += "<" + emoji_name + color_emoji[view.view[vy][vx]] + ">"
		return render[1:]
	
	def check(self, reaction, user):
		if self.msg:
			return user == self.author and str(reaction.emoji) in self.config["arrows"] and reaction.message.id == self.msg.id
		else:
			return False
	
	def add_msg(self, message):
		self.chat_buffer.append(message)
		if len(self.chat_buffer) > self.config["chat_buffer"]:
			self.chat_buffer.pop(0)
	
	async def start(self):
		if not self.ready and self.error:
			self.ctx.send(self.error)
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
		self.game_task = asyncio.ensure_future(self.loop())
	
	async def loop(self):
		timeout = 0
		while True:
			try:
				reaction, user = await self.bot.wait_for('reaction_add', check = self.check, timeout=2)
				timeout = 0
				emoji = reaction.emoji
				if emoji == self.config["arrows"][0]:
					#Left
					if not self.world.collide(self.data["pos_x"] -1, self.data["pos_y"]):
						self.data["pos_x"] -= 1
				elif emoji == self.config["arrows"][1]:
					#Up
					if not self.world.collide(self.data["pos_x"], self.data["pos_y"] -1):
						self.data["pos_y"] -= 1
				elif emoji == self.config["arrows"][2]:
					#Down
					if not self.world.collide(self.data["pos_x"], self.data["pos_y"] +1):
						self.data["pos_y"] += 1
				elif emoji == self.config["arrows"][3]:
					#Right
					if not self.world.collide(self.data["pos_x"] +1, self.data["pos_y"]):
						self.data["pos_x"] += 1
				view = self.get_view(self.data["pos_x"], self.data["pos_y"])
				render = self.render_view(view)
				if render != self.previous_render or len(self.chat_buffer) > 0 and self.last_msg != self.chat_buffer[-1].message:
					self.previous_render = render
					if len(self.chat_buffer) > 0:
						self.last_msg = self.chat_buffer[-1]
					embed = embeds.Embed(
						color=10038562,
						title="Legend",
						url="https://discordapp.com",
						description=render
						)
					for chat_msg in self.chat_buffer:
						s_time = chat_msg.time.strftime("%H:%M:%S")
						author_text = chat_msg.author + "#" + chat_msg.discriminator + " - " + s_time
						embed.add_field(name=author_text, value=chat_msg.message, inline=False)
					await self.msg.edit(embed=embed)
				await self.msg.remove_reaction(emoji, user)
			except asyncio.TimeoutError:
				timeout += 2
				if (timeout > 300):
					await self.disconnect("5 minutes of inactivity")
					break
				else:
					view = self.get_view(self.data["pos_x"], self.data["pos_y"])
					render = self.render_view(view)
					if render != self.previous_render or len(self.chat_buffer) > 0 and self.last_msg != self.chat_buffer[-1].message:
						self.previous_render = render
						if len(self.chat_buffer) > 0:
							self.last_msg = self.chat_buffer[-1]
						embed = embeds.Embed(
							color=10038562,
							title="Legend",
							url="https://discordapp.com",
							description=render
							)
						for chat_msg in self.chat_buffer:
							s_time = chat_msg.time.strftime("%H:%M:%S")
							author_text = chat_msg.author + "#" + chat_msg.discriminator + " - " + s_time
							embed.add_field(name=author_text, value=chat_msg.message, inline=False)
						await self.msg.edit(embed=embed)
	
	async def disconnect(self, reason=None):
		self.game_task.cancel()
		self.users.update_one( { "user": str(self.author.id) }, {"$set": self.data })
		if not reason:
			await self.msg.edit(content="❌ Disconnected", embed=None)
		else:
			await self.msg.edit(content="❌ Disconnected for " + reason, embed=None)
		return self.author

class LegendBot:
	def __init__(self, bot):
		global config
		self.config = config;
		self.bot = bot
		#Open the img in the world argument
		im = Image.open(self.config["world_map"])
		#Get image width and height for the world
		self.width, self.height = im.size

		#CONFIG: Screen width and height
		self.w_screen = self.config["screen_width"]
		self.h_screen = self.config["screen_height"]
		self.chat_radius = self.config["chat_radius"]
		self.max_buffer = self.config["chat_buffer"]

		#World list
		self.world_map = []
		self.bump_map = []
		self.messages = {}

		print("Loading " + self.config["world_map"] + " " + str(self.width) + " x " + str(self.height) + "\n")

		for y in range(self.height):
			#Loop over every line
			line = []
			for x in range(self.width):
				#Create a line variable for the x values, using their color index
				line.append(colors[im.getpixel((x,y))])
			#Add the line to the world
			#world[y][x]
			self.world_map.append(line)
		
		#Open the img in the bump argument
		im = Image.open(self.config["bump_map"])
		#Get image width and height for the world
		self.bump_width, self.bump_height = im.size
		if self.bump_width != self.width or self.bump_height != self.height:
			print("World/Bump Map MISMATCH!!!")
			exit()
		
		print("Loading " + self.config["bump_map"] + " " + str(self.bump_width) + " x " + str(self.bump_height) + "\n")

		for y in range(self.height):
			#Loop over every line
			line = []
			for x in range(self.width):
				#Create a line variable for the x values, using their color index
				line.append(bump_colors[im.getpixel((x,y))])
			#Add the line to the world
			#world[y][x]
			self.bump_map.append(line)

		#Turn it into a numpy array for 2d calculations and speed.
		self.world_map = numpy.array(self.world_map)
		self.bump_map = numpy.array(self.bump_map)
		self.world = World(self.world_map, self.bump_map)
		self.games = {}
		
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
			self.games[ctx.author.id].disconnect()
			self.games.pop(ctx.author.id)
		self.games[ctx.author.id] = LegendGame(ctx, self.config, self.users, self.world, self.games, self.bot)
		await self.games[ctx.author.id].start()
	
	@commands.command()
	async def say(self, ctx, *, msg):
		if ctx.author.id in self.games:
			await self.chat(ctx, msg, self.games[ctx.author.id])
		else:
			await ctx.send("You can only use this command ingame!")
	
	@commands.command()
	async def s(self, ctx, *, msg):
		if ctx.author.id in self.games:
			await self.chat(ctx, msg, self.games[ctx.author.id])
		else:
			await ctx.send("You can only use this command ingame!")
	
	@commands.command()
	async def tp(self, ctx, x : int, y : int):
		if ctx.author.id in self.games:
			self.games[ctx.author.id].data["pos_x"] = x
			self.games[ctx.author.id].data["pos_y"] = y
		else:
			await ctx.send("You can only use this command ingame!")
	
	@commands.command()
	async def stop(self, ctx):
		user_data = self.users.find_one({"user": str(ctx.author.id)})
		if user_data and "admin" in user_data and user_data["admin"] == True:
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
		
bot.remove_command("help")
bot.add_cog(LegendBot(bot))

@bot.event
async def on_ready():
	print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run(config["token"])