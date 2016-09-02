from kivy.properties import StringProperty

from ui.hex_widget import HexWidget


class Tile(HexWidget):
    debug_label = StringProperty('')

    def toggle_debug_label(self):
        if self.debug_label:
            self.debug_label = ''
        else:
            self.debug_label = '{0}, {1}'.format(self.hex_coords.q, self.hex_coords.r)
