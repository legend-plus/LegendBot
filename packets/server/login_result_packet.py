import struct

from packets.packet import Packet


class LoginResultPacket(Packet):

    name: str = "Login Result"
    id: int = 2

    def __init__(self, response_code: int, user_id: str = None):
        super().__init__()
        self.response_code: int = response_code
        self.user_id: str = user_id

    @classmethod
    def decode(cls, data: bytes):
        response_code = data[0]
        if len(data) > 1:
            user_id = data[1:].decode("utf-8")
            return cls(response_code, user_id)
        else:
            return cls(response_code)

    def encode(self) -> bytes:
        if self.user_id:
            return struct.pack(">B", self.response_code) + self.user_id.encode("utf-8")
        else:
            return struct.pack(">B", self.response_code)
