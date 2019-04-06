from packets.packet import Packet


class NullPacket(Packet):

    name: str = "Null"
    id: int = 0

    def __init__(self, data: bytes):
        super().__init__()
        self.data: bytes = data

    @classmethod
    def decode(cls, data: bytes):
        return cls(data)

    def encode(self) -> bytes:
        return self.data
