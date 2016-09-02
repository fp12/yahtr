from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window

from ui.game_view import GameView
from ui.class_list import create_class_list

from game import game_instance


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self._layout = None
        self.game_view = None
        self._key_binder = {}
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_unit_selected(self, adapter, *args):
        if len(adapter.selection) == 1:
            selected_class = adapter.selection[0].text
            if selected_class in game_instance.classes.keys():
                self.game_view.spawn_unit(selected_class)

    def on_start(self):
        game_instance.load()
        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size)
        self._key_binder.update({'d': [self.game_view.on_debug_key]})
        self._layout.add_widget(self.game_view)
        self._layout.add_widget(create_class_list(game_instance.classes, self.on_unit_selected))

    def build(self):
        self._layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.title = 'Yet Another Hex Tactical RPG'
        return self._layout

    def _on_keyboard_down(self, sdl_thing, code, thing, key, modifiers, *args):
        if key in self._key_binder:
            for cb in self._key_binder[key]:
                cb()
            return True
