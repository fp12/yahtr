from kivy.properties import NumericProperty
from ui.colored_widget import ColoredWidget

from hex_lib import Hex


class Hexagon(ColoredWidget):
    radius = NumericProperty(30)
    # front_radius = NumericProperty(5)

    def __init__(self, layout, q, r, **kwargs):
        self._layout = layout
        self._hex = Hex(q, r)
        self._color = [self.red, self.green, self.blue, self.alpha]
        super(Hexagon, self).__init__(pos=layout.hex_to_pixel(self._hex), **kwargs)
