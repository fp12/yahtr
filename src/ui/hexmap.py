from math import sqrt

from kivy.uix.relativelayout import RelativeLayout

from hex_lib import Layout
from game import game_instance
from ui.hexagon import Hexagon
from ui.unit import Unit


class HexMap(RelativeLayout):
    hex_radius = 30

    def __init__(self, **kwargs):
        super(HexMap, self).__init__(**kwargs)
        self._units_list = None
        self._layout = Layout(origin=(0, 0), size=HexMap.hex_radius, flat=game_instance.flat_layout, margin=2)
        self._unit = None
        self._hex_list = []

        Hexagon.radius = HexMap.hex_radius

        map_radius = 6
        for q in range(-map_radius, map_radius+1):
            r1 = max(-map_radius, -q - map_radius)
            r2 = min(map_radius, -q + map_radius)
            for r in range(r1, r2+1):
                hexagon = Hexagon(self._layout, q, r)
                self.add_widget(hexagon)
                self._hex_list.append(hexagon)

    def spawn_unit(self, unit):
        if self._unit:
            self._unit.clear()
            self.remove_widget(self._unit)
        self._unit = Unit(self._layout, game_instance.units[unit], 2, 2)
        self.add_widget(self._unit)
        self._unit.load()

    def on_debug_key(self):
        for x in self._hex_list:
                x.toggle_debug_label()

    def on_cycle_unit_action(self):
        if self._unit:
            self._unit.on_cycle_action()