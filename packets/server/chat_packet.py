import struct

from legendutils import ChatMessage
from packets.packet import Packet


class ChatPacket(Packet):

    name: str = "Chat"
    id: int = 7

    def __init__(self, msg: ChatMessage, x: int, y: int):
        super().__init__()
        self.author: str = msg.author
        self.msg: str = msg.message
        self.x: int = x
        self.y: int = y

    @classmethod
    def decode(cls, data: bytes):
        author_len = struct.unpack(">L", data[0:4])[0]
        author = data[4:4+author_len].decode("utf-8")
        msg_len = struct.unpack(">L", data[4+author_len:8+author_len])[0]
        msg = data[8+author_len:8+author_len+msg_len].decode("utf-8")
        x, y = struct.unpack(">LL", data[8+author_len+msg_len:16+author_len+msg_len])
        return cls(author, msg, x, y)

    def encode(self) -> bytes:
        output = b''
        encoded_author = self.author.encode("utf-8")
        encoded_msg = self.msg.encode("utf-8")

        output += struct.pack(">L", len(encoded_author))
        output += encoded_author
        output += struct.pack(">L", len(encoded_msg))
        output += encoded_msg
        output += struct.pack(">LL", self.x, self.y)

        return self.msg.encode("utf-8")
