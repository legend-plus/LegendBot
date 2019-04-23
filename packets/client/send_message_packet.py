from packets.packet import Packet


class SendMessagePacket(Packet):

    name: str = "Send Message"
    id: int = -7

    def __init__(self, msg: str):
        super().__init__()
        self.msg: str = msg

    @classmethod
    def decode(cls, data: bytes):
        return cls(data.decode("utf-8"))

    def encode(self) -> bytes:
        return self.msg.encode("utf-8")
