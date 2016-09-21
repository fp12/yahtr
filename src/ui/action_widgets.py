from kivy.properties import NumericProperty

from ui.colored_widget import ColoredWidget


class ActionArrow(ColoredWidget):
    angle = NumericProperty(0)

    def __init__(self, color=[1, 0, 0], **kwargs):
        super(ActionArrow, self).__init__(size_hint=(None, None), color=color, **kwargs)


class ActionUnitMove(ColoredWidget):
    angle = NumericProperty(0)
