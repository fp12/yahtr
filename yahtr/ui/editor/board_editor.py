from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty
from kivy.core.window import Window


class BoardEditor(TabbedPanelItem):
    text = 'Boards'
    grid = ObjectProperty()

    def __init__(self, **kwargs):
        super(BoardEditor, self).__init__(**kwargs)

        Window.bind(on_key_down=self.on_keyboard_down, mouse_pos=self.on_mouse_pos)

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers):
        pass

    def on_mouse_pos(self, *args):
        """dispatching mouse position by priority order"""
        if not self.get_root_window():
            return False

        self.grid.on_mouse_pos(*args)
