from abc import ABC, abstractmethod

from typing import List

from legendgame import LegendGame


class GuiResult(ABC):
    @abstractmethod
    def __init__(self):
        pass


class GuiOption(ABC):
    @abstractmethod
    def __init__(self, result: GuiResult):
        self.result = result


class Interaction(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def interact(self, game: LegendGame):
        pass


class DialogueResult(GuiResult):
    def __init__(self):
        super().__init__()
        pass


class DialogueOption(GuiOption):
    def __init__(self, text: str, result: DialogueResult):
        super().__init__(result)
        self.text = text  # type: str
        self.result = result  # type: DialogueResult


class DialogueMessage:
    def __init__(self, author: str, text: str, sprite: str):
        self.author = author
        self.text = text
        self.sprite = sprite


class Dialogue(Interaction):
    def __init__(self, author: str, text: str, sprite: str, options: List[DialogueOption]):
        super().__init__()
        self.text = text
        self.author = author
        self.options = options

    def interact(self, game: LegendGame):
        game.paused = True
        game.gui_options = self.options
        gui_description = ""

        for x in range(min(len(game.config["arrows"]), len(self.options))):
            if x > 0:
                gui_description += "\n"
            gui_description += game.config["arrows"][x] + " " + self.options[x].text

        game.gui_description = gui_description
        game.dialogue_buffer = DialogueMessage(self.author, self.text, self.sprite)
        return True
