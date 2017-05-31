from math import pi, cos, sin

from kivy.properties import NumericProperty, ListProperty

from yahtr.ui.base_widgets import ColoredWidget

from yahtr.core.hex_lib import Hex


class HexWidget(ColoredWidget):
    radius = NumericProperty(30)
    coss = ListProperty([cos(pi / 3 * i) for i in range(6)])
    sins = ListProperty([sin(pi / 3 * i) for i in range(6)])

    def __init__(self, q=0, r=0, layout=None, radius=None, **kwargs):
        self.hex_coords = Hex(q, r)
        self.hex_layout = layout
        self.radius = radius or layout.size.x if layout else 0

        super(HexWidget, self).__init__(size_hint=(None, None), **kwargs)
        self.pos = layout.hex_to_pixel(self.hex_coords).tup if layout and self.hex_coords else self.pos

    def setup(self, q, r, layout, radius=None):
        self.hex_coords = Hex(q, r)
        self.hex_layout = layout
        self.radius = radius or layout.size.x if layout else 0
        self.pos = layout.hex_to_pixel(self.hex_coords)

    def move_to(self, hex_coords, tile_pos=None, trajectory=None):
        self.hex_coords = hex_coords
        self.pos = tile_pos or self.hex_layout.hex_to_pixel(self.hex_coords)
