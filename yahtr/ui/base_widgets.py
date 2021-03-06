from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget

from yahtr.utils import Color


class AngledWidget(Widget):
    angle = NumericProperty(0)
    rotate_from_center = BooleanProperty(False)


class ColoredWidget(Widget):
    r = NumericProperty(1.)
    g = NumericProperty(1.)
    b = NumericProperty(1.)
    a = NumericProperty(1.)

    def __init__(self, color=None, **kwargs):
        if color:
            self.color = color
        self.old_a = self.a
        super(ColoredWidget, self).__init__(**kwargs)

    @property
    def color(self):
        return [self.r, self.g, self.b, self.a]

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            value = value.color
        if len(value) == 3:
            value.append(self.a)
        self.r, self.g, self.b, self.a = value

    @property
    def hidden(self):
        return self.a == 0

    def hide(self, do_hide=True):
        if do_hide:
            self.old_a = self.a
        self.a = 0 if do_hide else self.old_a

    def show(self):
        self.a = self.old_a

    def on_color_change(self, r, g, b, a):
        pass

    def on_r(self, *args):
        self.on_color_change(self.r, self.g, self.b, self.a)

    def on_g(self, *args):
        self.on_color_change(self.r, self.g, self.b, self.a)

    def on_b(self, *args):
        self.on_color_change(self.r, self.g, self.b, self.a)

    def on_a(self, *args):
        self.on_color_change(self.r, self.g, self.b, self.a)


class AngledColoredWidget(ColoredWidget, AngledWidget):
    pass
