from kivy.properties import NumericProperty, StringProperty

from ui.colored_widget import ColoredWidget

from hex_lib import Hex


class Hexagon(ColoredWidget):
    radius = NumericProperty(30)
    debug_label = StringProperty('')

    def __init__(self, layout, q, r, **kwargs):
        self._layout = layout
        self._hex = Hex(q, r)
        self._color = [self.red, self.green, self.blue, self.alpha]
        super(Hexagon, self).__init__(center=layout.hex_to_pixel(self._hex), size_hint=(None, None), **kwargs)

    def toggle_debug_label(self):
        if self.debug_label:
            self.debug_label = ''
        else:
            self.debug_label = '{0}, {1}'.format(self._hex.q, self._hex.r)
