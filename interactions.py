from abc import ABC, abstractmethod

from typing import List, Tuple
import requirements
from items import Item


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
    def __init__(self, text: str, result: GuiResult, reqs=None):
        super().__init__(result)
        if reqs is None:
            reqs = []
        self.text: str = text
        self.result: GuiResult = result
        self.reqs: List[requirements.Requirement] = reqs


class DialogueMessage:
    def __init__(self, author: str, text: str, sprite: str):
        self.author = author
        self.text = text
        self.sprite = sprite


class Dialogue(Interaction):
    def __init__(self, author: str, text: str, sprite: str, options: List[DialogueOption], items: List[Tuple[Item, bool]]=None,
                 flags: List[requirements.FlagOperation] = None):
        super().__init__()
        if items is None:
            items = []
        if flags is None:
            flags = []
        self.text = text
        self.author = author
        self.options: List[DialogueOption] = options
        self.sprite = sprite
        self.items: List[Tuple[Item, bool]] = items
        self.flags = flags

    def interact(self, session):
        session.mode = "dialogue"
        session.gui_options = []  # self.options
        num_options = 0
        gui_description: str = ""

        if hasattr(session, "config") and "arrows" in session.config:
            for opt in self.options:
                if num_options < len(session.config["arrows"]):
                    add_option: bool = True
                    for requirement in opt.reqs:
                        if not requirement.validate(session.data["flags"]):
                            add_option = False
                    if add_option:
                        session.gui_options.append(opt)
                        if num_options > 0:
                            gui_description += "\n"
                        gui_description += session.config["arrows"][num_options] + " " + opt.text
                        num_options += 1
        r = 0
        while self.text.find("%item") != -1:
            self.text = self.text.replace("%item", "**[" + session.sprites["items"][self.items[r][0].get_sprite(session.base_items)] + " " + self.items[r][0].get_name(session.base_items) + "]**", 1)
            r += 1

        for dialogue_item in self.items:
            if dialogue_item[1]:
                session.data["inventory"].append(dialogue_item[0])

        for flag in self.flags:
            flag.apply(session.data["flags"])

        session.gui_description = gui_description
        session.dialogue_buffer = DialogueMessage(self.author, self.text, self.sprite)
        return True
