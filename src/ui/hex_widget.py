from math import pi, cos, sin

from kivy.properties import NumericProperty, ListProperty

from ui.colored_widget import ColoredWidget

from hex_lib import Hex


class HexWidget(ColoredWidget):
    radius = NumericProperty(30)
    coss = ListProperty([cos(pi / 3 * i) for i in range(6)])
    sins = ListProperty([sin(pi / 3 * i) for i in range(6)])

    def __init__(self, q, r, layout, radius=None, **kwargs):
        self.hex_coords = Hex(q, r)
        self.hex_layout = layout
        self.radius = radius or layout.size.x

        hex_pos = layout.hex_to_pixel(self.hex_coords)
        super(HexWidget, self).__init__(pos=(hex_pos.x, hex_pos.y), size_hint=(None, None), **kwargs)

    def move_to(self, hex_coords, tile_pos=None, trajectory=[], on_move_end=None):
        self.hex_coords = hex_coords
        self.pos = tile_pos or self.hex_layout.hex_to_pixel(self.hex_coords)
        if on_move_end:
            on_move_end()
