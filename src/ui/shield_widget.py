from kivy.properties import NumericProperty
from ui.hex_widget import HexWidget


class ShieldWidget(HexWidget):
    thickness = NumericProperty(3)
    angle = NumericProperty(0)
