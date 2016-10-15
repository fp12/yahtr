from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget


class AngledWidget(Widget):
    angle = NumericProperty(0)
    rotate_from_center = BooleanProperty(False)


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

    @property
    def hidden(self):
        return self.a == 0

    def hide(self, do_hide=True):
        self.a = 0 if do_hide else 1

    def restore_old_color(self):
        if self._old_color:
            self.r, self.g, self.b, self.a = self._old_color
        self._old_color = None

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
