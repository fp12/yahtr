from kivy.properties import NumericProperty

from yahtr.ui.hex_widget import HexWidget
from yahtr.ui.base_widgets import AngledWidget


class ShieldWidget(HexWidget, AngledWidget):
    thickness = NumericProperty(3)
