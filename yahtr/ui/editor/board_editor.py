from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty
from kivy.core.window import Window

from yahtr.board import save_one_board_template


class BoardEditor(TabbedPanelItem):
    text = 'Boards'
    grid = ObjectProperty()

    def __init__(self, **kwargs):
        super(BoardEditor, self).__init__(**kwargs)
        self.data = None

        Window.bind(on_key_down=self.on_keyboard_down, mouse_pos=self.on_mouse_pos)

    def set_active(self, data):
        self.data = data
        self.grid.load_grid(data.tiles)

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers):
        if 'ctrl' in modifiers and text == 's':
            self.data.tiles = self.grid.content_hexes
            save_one_board_template(self.data)

    def on_mouse_pos(self, *args):
        """dispatching mouse position by priority order"""
        if not self.get_root_window():
            return False

        self.grid.on_mouse_pos(*args)
