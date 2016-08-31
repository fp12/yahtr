from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class ColoredWidget(Widget):
    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)
    a = NumericProperty(1)

    def __init__(self, color=None, **kwargs):
        if color:
            self.color = color
        super(ColoredWidget, self).__init__(**kwargs)
        self._old_color = self.color

    @property
    def color(self):
        return [self.r, self.g, self.b, self.a]

    @color.setter
    def color(self, value):
        if len(value) == 3:
            value = value + [self.a]
        self._old_color = [self.r, self.g, self.b, self.a]
        self.r, self.g, self.b, self.a = value

    def restore_old_color(self):
        if self._old_color:
            self.r, self.g, self.b, self.a = self._old_color
        self._old_color = []

    def hide(self, do_hide=True):
        self.a = 0 if do_hide else 1
