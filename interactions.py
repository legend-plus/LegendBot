from abc import ABC, abstractmethod

from typing import List


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
    def interact(self, session):
        pass


class CloseGuiResult(GuiResult):
    def __init__(self):
        super().__init__()


class ContinueDialogueResult(GuiResult):
    def __init__(self, dialogue_id: str):
        super().__init__()
        self.dialogue_id = dialogue_id


class DialogueOption(GuiOption):
    def __init__(self, text: str, result: GuiResult):
        super().__init__(result)
        self.text: str = text
        self.result: GuiResult = result


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
        self.sprite = sprite

    def interact(self, session):
        session.mode = "dialogue"
        session.gui_options = self.options
        gui_description: str = ""

        if hasattr(session, "config") and "arrows" in session.config:
            for x in range(min(len(session.config["arrows"]), len(self.options))):
                if x > 0:
                    gui_description += "\n"
                gui_description += session.config["arrows"][x] + " " + self.options[x].text

        session.gui_description = gui_description
        session.dialogue_buffer = DialogueMessage(self.author, self.text, self.sprite)
        return True
