import collections

from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window

from hex_lib import Layout, Hex
from game import game_instance
from ui.hexagon import Hexagon
from ui.unit import Unit


HoverInfo = collections.namedtuple('HoverInfo', ['widget', 'old_color'])


class HexMap(ScatterLayout):
    hex_radius = 30

    def __init__(self, **kwargs):
        self.hex_layout = None
        super(HexMap, self).__init__(**kwargs)
        self._units_list = None
        self.hex_layout = Layout(origin=self.center, size=HexMap.hex_radius, flat=game_instance.flat_layout, margin=2)
        self._unit = None
        self.tiles = []

        Hexagon.radius = HexMap.hex_radius

        map_radius = 6
        for q in range(-map_radius, map_radius + 1):
            r1 = max(-map_radius, -q - map_radius)
            r2 = min(map_radius, -q + map_radius)
            for r in range(r1, r2 + 1):
                hexagon = Hexagon(self.hex_layout, q, r, size=(HexMap.hex_radius, HexMap.hex_radius))
                self.add_widget(hexagon)
                self.tiles.append(hexagon)

        Window.bind(mouse_pos=self.on_mouse_pos)
        self._hover_info = None

    def spawn_unit(self, selected_class):
        if self._unit:
            self._unit.clear()
            self.remove_widget(self._unit)
        self._unit = Unit(self.hex_layout, game_instance.classes[selected_class], q=0, r=0)
        self.add_widget(self._unit)
        self._unit.load()

    def on_debug_key(self):
        for x in self.tiles:
            x.toggle_debug_label()

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        # get rounded hex coordinates
        hover_hex = self.hex_layout.pixel_to_hex(pos).get_round()
        if self._hover_info and self._hover_info.widget._hex == hover_hex:
            return
        for tile in self.tiles:
            if tile._hex == hover_hex:
                # reset the old hovered tile
                if self._hover_info:
                    self._hover_info.widget.color = self._hover_info.old_color
                # store old info and set new color
                self._hover_info = HoverInfo(tile, tile.color)
                tile.color = [0.560784, 0.737255, 0.560784, 1]
                return True
        # if we aren't on a tile, we reset the hovered tile
        if self._hover_info:
            self._hover_info.widget.color = self._hover_info.old_color
            self._hover_info = None
    
    def on_touch_down(self, touch):
        if self._unit and self._hover_info:
            if self._hover_info.widget._hex == self._unit._hex:
                return self._unit.on_real_touch_down()
            else:
                self._unit.move_to(self._hover_info.widget._hex, self._hover_info.widget.pos)
                return True
