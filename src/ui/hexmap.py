from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window

from hex_lib import Layout, Hex
from game import game_instance
from ui.hexagon import Hexagon
from ui.unit import Unit


class HexMap(ScatterLayout):
    hex_radius = 30

    def __init__(self, **kwargs):
        self.hex_layout = None
        super(HexMap, self).__init__(**kwargs)
        self._units_list = None
        self.hex_layout = Layout(origin=self.center, size=HexMap.hex_radius, flat=game_instance.flat_layout, margin=2)
        self._unit = None
        self._hex_list = []

        Hexagon.radius = HexMap.hex_radius

        map_radius = 6
        for q in range(-map_radius, map_radius + 1):
            r1 = max(-map_radius, -q - map_radius)
            r2 = min(map_radius, -q + map_radius)
            for r in range(r1, r2 + 1):
                hexagon = Hexagon(self.hex_layout, q, r, size=(HexMap.hex_radius, HexMap.hex_radius))
                self.add_widget(hexagon)
                self._hex_list.append(hexagon)

        Window.bind(mouse_pos=self.on_mouse_pos)
        self._mouse_over_hex = None

    def spawn_unit(self, selected_class):
        if self._unit:
            self._unit.clear()
            self.remove_widget(self._unit)
        self._unit = Unit(self.hex_layout, game_instance.units[selected_class], q=-1, r=2)
        self.add_widget(self._unit)
        self._unit.load()

    def on_debug_key(self):
        for x in self._hex_list:
            x.toggle_debug_label()

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        """
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and not self._mouse_over_hex:
            print(self._hex)
            self._mouse_over_hex = True
            if self.red > 0:
                self.red = self.red / 2
            else:
                self.red = self.red * 2
        elif not inside and self._mouse_over_hex:
            self.ref = 1
        """
