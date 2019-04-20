import struct
import uuid

from legendutils import ChatMessage
from packets.packet import Packet


class ChatPacket(Packet):

    name: str = "Chat"
    id: int = 7

    def __init__(self, msg: ChatMessage, x: int, y: int):
        super().__init__()
        self.author: str = msg.author
        self.user_id: str = msg.user_id
        self.msg_id: str = msg.uuid
        self.msg: str = msg.message
        self.x: int = x
        self.y: int = y

    @classmethod
    def decode(cls, data: bytes):
        author_len = struct.unpack(">L", data[0:4])[0]
        author = data[4:4+author_len].decode("utf-8")

        msg_len = struct.unpack(">L", data[4+author_len:8+author_len])[0]
        msg = data[8+author_len:8+author_len+msg_len].decode("utf-8")

        user_len = struct.unpack(">L", data[8+author_len+msg_len:12+author_len+msg_len])[0]
        user_id = data[12+author_len+msg_len:12+author_len+msg_len+user_len].decode("utf-8")

        msg_uuid = uuid.UUID(data[12+author_len+msg_len+user_len:44+author_len+msg_len+user_len].decode("utf-8"))
        x, y = struct.unpack(">ll", data[44+author_len+msg_len+user_len:48+author_len+msg_len+user_len])

        chat_msg = ChatMessage(author, msg, user_id, msg_uuid)
        return cls(chat_msg, x, y)

    def encode(self) -> bytes:
        output = b''
        encoded_author = self.author.encode("utf-8")
        encoded_msg = self.msg.encode("utf-8")
        encoded_id = str(self.user_id).encode("utf-8")
        encoded_msg_id = self.msg_id.encode("utf-8")

        output += struct.pack(">L", len(encoded_author))
        output += encoded_author

        output += struct.pack(">L", len(encoded_msg))
        output += encoded_msg

        output += struct.pack(">L", len(encoded_id))
        output += encoded_id

        output += encoded_msg_id

        output += struct.pack(">ll", self.x, self.y)

        return output
