from kivy.properties import NumericProperty, StringProperty

from ui.colored_widget import ColoredWidget

from hex_lib import Hex


class Hexagon(ColoredWidget):
    radius = NumericProperty(30)
    debug_label = StringProperty('')

    def __init__(self, layout, q, r, **kwargs):
        self.hex_layout = layout
        self._hex = Hex(q, r)
        hex_pos = layout.hex_to_pixel(self._hex)
        super(Hexagon, self).__init__(pos=(hex_pos.x, hex_pos.y), color=[0.9, 0.9, 0.9, 1], size_hint=(None, None), **kwargs)

    def move_to(self, hex_coords, tile_pos=None):
        self._hex = hex_coords
        self.pos = tile_pos or self.hex_layout.hex_to_pixel(self._hex)

    def toggle_debug_label(self):
        if self.debug_label:
            self.debug_label = ''
        else:
            self.debug_label = '{0}, {1}'.format(self._hex.q, self._hex.r)
