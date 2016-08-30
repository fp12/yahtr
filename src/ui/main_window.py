from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window

from ui.hexmap import HexMap
from ui.units_list import create_units_list

from game import game_instance


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self._layout = None
        self._map = None
        self._key_binder = {}
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_unit_selected(self, adapter, *args):
        if len(adapter.selection) == 1:
            unit = adapter.selection[0].text
            if unit in game_instance.units.keys():
                self._map.spawn_unit(unit)

    def on_start(self):
        game_instance.load()
        self._map = HexMap(pos=(0, 0), size_hint=(None, None), size=Window.size)
        self._key_binder.update({'d': [self._map.on_debug_key]})
        self._layout.add_widget(self._map)
        self._layout.add_widget(create_units_list(game_instance.units, self.on_unit_selected))

    def build(self):
        self._layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.title = 'Yet Another Hex Tactical RPG'
        return self._layout

    def _on_keyboard_down(self, sdl_thing, code, thing, key, modifiers, *args):
        if key in self._key_binder:
            for cb in self._key_binder[key]:
                cb()
            return True
