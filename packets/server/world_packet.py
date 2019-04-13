import struct

from packets.packet import Packet


class WorldPacket(Packet):

    name: str = "World"
    id: int = 3

    def __init__(self, height: int, width: int, world: bytes, world_word_size: int, bump_world: bytes, bump_word_size: int):
        super().__init__()
        self.height = height
        self.width = width
        self.world = world
        self.world_word_size = world_word_size
        self.bump_world = bump_world
        self.bump_word_size = bump_word_size

    @classmethod
    def decode(cls, data: bytes):
        height: int = struct.unpack(">L", data[0:4])[0]
        width: int = struct.unpack(">L", data[4:8])[0]
        world_size: int = struct.unpack(">L", data[8:12])[0]
        world: bytes = data[12:12+world_size]
        world_word_size: int = struct.unpack(">L", data[12+world_size:16+world_size])[0]
        bump_size: int = struct.unpack(">L", data[16+world_size:20+world_size])[0]
        bump_world: bytes = data[20+world_size:20+world_size+bump_size]
        bump_word_size: int = struct.unpack(">L", data[20+world_size+bump_size:24+world_size+bump_size])[0]
        return cls(height, width, world, world_word_size, bump_world, bump_word_size)

    def encode(self) -> bytes:
        output = b''
        output += struct.pack(">L", self.height)
        output += struct.pack(">L", self.width)

        output += struct.pack(">L", len(self.world))
        output += self.world
        output += struct.pack(">L", self.world_word_size)

        output += struct.pack(">L", len(self.bump_world))
        output += self.bump_world
        output += struct.pack(">L", self.bump_word_size)
        return output
