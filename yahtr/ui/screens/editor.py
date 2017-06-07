from enum import Enum

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import yahtr.ui.selectable_recycle_box_layout  # force import needed for kv files :(
from yahtr.ui.utils import find_id
from yahtr.game_data import game_data


Builder.load_file('yahtr/ui/kv/editor.kv')


class TabData(Enum):
    actions_trees = 0
    skills = 1
    weapons_templates = 2
    units_templates = 3
    boards = 4
    battle_setups = 5


class Editor(Screen):
    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.tab_data = TabData.actions_trees
        self.refresh_rv()
        self.rv_layout.on_selection += self.on_data_change

    def refresh_rv(self):
        self.rv.data = [{'value': data.id} for data in getattr(game_data, self.tab_data.name)]
        self.rv_layout.clear_selection()

    def on_tab_change(self, widget):
        self.tab_data = TabData[find_id(self.tp, widget)]
        self.refresh_rv()

    def on_data_change(self, id, value):
        pass
