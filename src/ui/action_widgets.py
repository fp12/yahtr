from kivy.properties import NumericProperty

from ui.colored_widget import AngledColoredWidget


class ActionArrow(AngledColoredWidget):
    def __init__(self, color=[1, 0, 0], **kwargs):
        super(ActionArrow, self).__init__(size_hint=(None, None), color=color, **kwargs)


class ActionUnitMove(AngledColoredWidget):
    pass


class ActionNMIMove(AngledColoredWidget):
	origin_x = NumericProperty()
	origin_y = NumericProperty()
