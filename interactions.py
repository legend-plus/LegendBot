from typing import List

from legendgame import LegendGame


class DialogueResult:
    def __init__(self):
        pass


class DialogueOption:
    def __init__(self, text: str, label: str, result: DialogueResult):
        self.text = text  # type: str
        self.label = label  # type: str
        self.result = result  # type: DialogueResult


class Interaction:
    def __init__(self):
        pass


class Dialogue(Interaction):
    def __init__(self, text: str, options: List[DialogueOption]):
        super().__init__()
        self.text = text
        self.options = options
