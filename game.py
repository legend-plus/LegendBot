from abc import ABC, abstractmethod

from entities import Entity

class Game(Entity):
    ready: bool
    running: bool
    paused: bool
    gui_options:  list
    chat_buffer: list
    dialogue_buffer: list
    gui_description: str

    def __init__(self, pos_x: int, pos_y: int):
        super().__init__("player", pos_x, pos_y, "")
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
    def add_msg(self, msg) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self, reason: str = None) -> bool:
        pass
