from yahtr.ui.base_widgets import AngledColoredWidget

from yahtr.utils import Color
from yahtr.wall import WallType


class WallWidget(AngledColoredWidget):
    color_solid = Color(1., 1., 1., 1.)
    color_breakable = Color(0.6, 0.6, 0.6, 1.)

    def __init__(self, wall, **kwargs):
        self.origin = wall.origin
        self.destination = wall.destination
        self.types = wall.types
        super(WallWidget, self).__init__(color=self.get_default_color(), **kwargs)

    def get_default_color(self):
        return self.color_breakable if WallType.breakable in self.types else self.color_solid
