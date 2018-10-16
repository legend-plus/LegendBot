from datetime import datetime
import numpy
import uuid

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