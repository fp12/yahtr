from kivy.properties import NumericProperty

from ui.hex_widget import HexWidget


class Selector(HexWidget):
    margin = NumericProperty(2)

    def __init__(self, margin=None, **kwargs):
        super(Selector, self).__init__(**kwargs)
        self.margin = margin or self.hex_layout.margin
