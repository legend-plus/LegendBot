from typing import List, Dict

import items
import copy
from game import Game
from interactions import GuiOption, DialogueMessage, CloseGuiResult, ContinueDialogueResult, Dialogue
from legendutils import View, ChatMessage, World
from math import ceil, floor, modf

inv_filters: List[str] = ["all", "weapon", "consumable", "quest"]


class Inventory:
    def __init__(self, inv_items: List[items.Item], base_items, config):
        self.items: List[items.Item] = inv_items
        self.view: List[items.Item] = inv_items
        self.cursor: int = 0
        self.screen_cursor: int = 0
        self.filter_index: int = 0
        self.base_items: Dict[str, dict] = base_items
        self.inv_display: List[items.Item] = []
        self.config = config
        self.get_view()

    def add_item(self, item: items.Item):
        self.items.append(item)
        self.set_filter(self.get_filter())
        self.get_view()

    def remove_item_index(self, index: int):
        self.items.pop(index)
        self.set_filter(self.get_filter())
        self.get_view()

    def remove_item(self, item: items.Item):
        for x in range(len(self.items)):
            if self.items[x] == item:
                self.items.pop(x)
                self.set_filter(self.get_filter())
                self.get_view()
                return True
        else:
            return False

    def set_filter(self, inv_filter: str):
        self.view: List[items.Item] = []
        for item in self.items:
            if item.get_item_type(self.base_items) == inv_filter or inv_filter == "all":
                self.view.append(item)

    def get_filter(self):
        return inv_filters[self.filter_index]

    def get_range(self, start: int, end: int) -> List[items.Item]:
        inv_range: List[items.Item] = self.items[start:end]
        return inv_range

    def get_view(self):
        cursor_min: int = int(max(0, self.screen_cursor))
        self.inv_display: List[items.Item] = self.view[cursor_min:cursor_min + self.config["items_per_page"]]

    def next_filter(self):
        if self.filter_index + 1 < len(inv_filters):
            self.filter_index += 1
        else:
            self.filter_index = 0
        self.cursor = 0
        self.screen_cursor = 0
        self.set_filter(self.get_filter())
        self.get_view()

    def prev_filter(self):
        if self.filter_index > 0:
            self.filter_index -= 1
        else:
            self.filter_index = len(inv_filters) - 1
        self.cursor = 0
        self.screen_cursor = 0
        self.set_filter(self.get_filter())
        self.get_view()

    def cursor_down(self):
        if self.cursor + 1 < len(self.view):
            self.cursor += 1
        else:
            self.cursor = 0
            self.screen_cursor = 0
        if self.cursor >= self.screen_cursor + self.config["items_per_page"]:
            self.screen_cursor = self.cursor - self.config["items_per_page"] + 1
        self.get_view()

    def cursor_up(self):
        if self.cursor > 0:
            self.cursor -= 1
        else:
            self.cursor = len(self.view) - 1
            self.screen_cursor = self.cursor - self.config["items_per_page"] + 1
        if self.cursor < self.screen_cursor:
            self.screen_cursor = self.cursor
        self.get_view()
