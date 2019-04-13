from packets.packet import Packet


class LoginPacket(Packet):

    name: str = "Login"
    id: int = -2

    def __init__(self, access_token: str):
        super().__init__()
        self.access_token: str = access_token

    @classmethod
    def decode(cls, data: bytes):
        return cls(data.decode("utf-8"))

    def encode(self) -> bytes:
        return self.access_token.encode("utf-8")
