from abc import ABC, abstractmethod


class Packet(ABC):

    name: str = "Null"
    id: int = 0

    @abstractmethod
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes):
        pass

    @abstractmethod
    def encode(self) -> bytes:
        pass
