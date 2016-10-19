from ui.base_widgets import AngledColoredWidget

from utils import Color
from game_map import WallType


class WallWidget(AngledColoredWidget):
    color_solid = Color(0.9, 0.9, 0.9, 0.9)
    color_breakable = Color(0.9, 0.9, 0.9, 0.9)

    def __init__(self, wall, **kwargs):
        self.origin = wall.origin
        self.destination = wall.destination
        color = self.color_breakable if WallType.breakable in wall.types else self.color_solid
        super(WallWidget, self).__init__(color=color, **kwargs)
