from abc import ABC, abstractmethod


class Game(ABC):
    ready: bool
    running: bool
    paused: bool
    gui_options:  list
    chat_buffer: list
    dialogue_buffer: list
    gui_description: str

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def update_screen(self, render: str) -> None:
        pass

    @abstractmethod
    def move(self, x: int, y: int, force: bool = False) -> bool:
        pass

    @abstractmethod
    def gui_interact(self, choice: int) -> None:
        pass

    @abstractmethod
    def add_msg(self) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self, reason: str = None) -> bool:
        pass
