from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class ColoredWidget(Widget):
    red = NumericProperty(1)
    green = NumericProperty(1)
    blue = NumericProperty(1)
    alpha = NumericProperty(1)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if len(value) == 3:
            value = value + [self.alpha]
        self._color = value
        self.red, self.green, self.blue, self.alpha = value
