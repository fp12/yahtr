from kivy.properties import NumericProperty

from ui.hex_widget import HexWidget
from ui.base_widgets import AngledWidget


class ShieldWidget(HexWidget, AngledWidget):
    thickness = NumericProperty(3)
