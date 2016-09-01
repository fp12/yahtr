from math import pi, cos, sin

from kivy.properties import NumericProperty, StringProperty, ListProperty

from ui.colored_widget import ColoredWidget

from hex_lib import Hex


class HexWidget(ColoredWidget):
    radius = NumericProperty(30)
    debug_label = StringProperty('')
    coss = ListProperty([cos(pi/3 * i) for i in range(6)])
    sins = ListProperty([sin(pi/3 * i) for i in range(6)])

    def __init__(self, q, r, layout, **kwargs):
        self.hex_coords = Hex(q, r)
        self.hex_layout = layout
        self.radius = layout.size.x

        hex_pos = layout.hex_to_pixel(self.hex_coords)
        super(HexWidget, self).__init__(pos=(hex_pos.x, hex_pos.y), size_hint=(None, None), **kwargs)

    def move_to(self, hex_coords, tile_pos=None):
        self.hex_coords = hex_coords
        self.pos = tile_pos or self.hex_layout.hex_to_pixel(self.hex_coords)

    def toggle_debug_label(self):
        if self.debug_label:
            self.debug_label = ''
        else:
            self.debug_label = '{0}, {1}'.format(self.hex_coords.q, self.hex_coords.r)
