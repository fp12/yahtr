from kivy.properties import StringProperty, ListProperty

from yahtr.ui.hex_widget import HexWidget


class Tile(HexWidget):
    debug_label = StringProperty('')
    line_rgba = ListProperty((0, 0, 0, 0))

    def __init__(self, line_rgba=None, **kwargs):
        self.line_rgba = line_rgba if line_rgba else [0, 0, 0, 0]
        super(Tile, self).__init__(**kwargs)

    def toggle_debug_label(self):
        if self.debug_label:
            self.debug_label = ''
        else:
            self.debug_label = f'{self.hex_coords.q}, {self.hex_coords.r}'
