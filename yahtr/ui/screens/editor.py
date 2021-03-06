from enum import Enum

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import yahtr.ui.selectable_recycle_box_layout  # force import needed for kv files :(
import yahtr.ui.hex_grid  # force import needed for kv files :(
import yahtr.ui.editor.board_editor  # force import needed for kv files :(
from yahtr.ui.utils import find_id
from yahtr.data.bank import data_bank


Builder.load_file('yahtr/ui/kv/editor.kv')


class TabData(Enum):
    actions_trees = 0
    skills = 1
    weapon_templates = 2
    unit_templates = 3
    board_templates = 4
    battle_setups = 5


class Editor(Screen):
    screen_name = 'main_menu'

    def __init__(self, **kwargs):
        super(Editor, self).__init__(name=Editor.screen_name, **kwargs)
        self.tab_data = TabData.actions_trees
        self.rv_layout.on_selection += self.on_data_change

    def on_enter(self):
        data_bank.load_all()
        self.refresh_rv()

    def on_pre_leave(self):
        data_bank.unload_all()

    def refresh_rv(self):
        self.rv.data = [{'value': data.file_id} for data in getattr(data_bank, self.tab_data.name)]
        self.rv_layout.clear_selection()

    def on_tab_change(self, widget):
        self.tab_data = TabData[find_id(self.tp, widget)]
        self.refresh_rv()

    def on_data_change(self, instance, value):
        if self.tab_data is TabData.actions_trees:
            data = data_bank.get_actions_tree(value)
            if data:
                self.tp.current_tab.title.text = repr(data)
        elif self.tab_data is TabData.board_templates:
            data = data_bank.get_board_template(value)
            if data:
                self.tp.current_tab.set_active(data)
