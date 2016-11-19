from ui.base_widgets import AngledColoredWidget

from utils import Color
from wall import WallType


class WallWidget(AngledColoredWidget):
    color_solid = Color(1., 1., 1., 1.)
    color_breakable = Color(0.6, 0.6, 0.6, 1.)

    def __init__(self, wall, **kwargs):
        self.origin = wall.origin
        self.destination = wall.destination
        color = self.color_breakable if WallType.breakable in wall.types else self.color_solid
        super(WallWidget, self).__init__(color=color, **kwargs)
