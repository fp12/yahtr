""" Reference for color names and definitions: http://www.avatar.se/molscript/doc/colour_names.html
    This list is never accessed directly but through Color('white') or even Color.white
"""
colors = {
    'black': (0, 0, 0),
    'white': (1., 1., 1.),
    'red': (1., 0, 0),
    'green': (0, 1., 0),
    'blue': (0, 0, 1.),
    'firebrick': (0.698039, 0.133333, 0.133333),
    'forestgreen': (0.133333, 0.545098, 0.13333),
    'olivedrab': (0.419608, 0.556863, 0.137255),
    'darkseagreen': (0.560784, 0.737255, 0.560784),
    'lightgreen': (0.564706, 0.933333, 0.564706),
    'player_team': (0, 88, 209),
    'ai_team_1': (217, 42, 22),
    'action_move_rotate': (57, 127, 191),
    'action_weapon': (68, 152, 229),
    'action_skill': (76, 169, 255),
    'action_endturn': (38, 85, 127)
}


class __MetaColor(type):
    pass


class Color(metaclass=__MetaColor):
    def __init__(self, *args, **kwargs):
        self.color = [0, 0, 0, 1.]

        name = args[0] if args else None
        if name and isinstance(name, str) and name in colors:
            self.set_rgb(*colors[name])
        else:
            self.set_rgb(*args, **kwargs)

    def _to_float(self, value):
        if value != 0 and isinstance(value, int):
            value /= 255
        return value

    def set_rgb(self, *args, **kwargs):
        color = kwargs.get('rgb') or kwargs.get('rgba') or list(args)
        if color and isinstance(color, (list, tuple)):
            if len(color) == 3:
                self.color = [self._to_float(x) for x in color] + [self.color[3]]
            elif len(color) == 4:
                self.color = [self._to_float(x) for x in color]
            else:
                raise AttributeError('`color` attribute (`{}`) has {} elements'.format(color, len(color)))
        else:
            # Todo: manage kwargs (r, g, b, a)
            pass

    @property
    def r(self):
        return self.color[0]

    @r.setter
    def r(self, value):
        self.color[0] = value

    @property
    def g(self):
        return self.color[1]

    @g.setter
    def g(self, value):
        self.color[1] = value

    @property
    def b(self):
        return self.color[2]

    @b.setter
    def b(self, value):
        self.color[2] = value

    @property
    def a(self):
        return self.color[3]

    @a.setter
    def a(self, value):
        self.color[3] = value

    @property
    def rgb(self):
        return self.color[:3]

    @property
    def rgb_dict(self):
        return {'r': self.color[0], 'g': self.color[1], 'b': self.color[2]}


def __add_metacolor_property(name, value):
    def inner(self):
        return Color(*value)
    inner.__name__ = name
    setattr(__MetaColor, inner.__name__, property(inner))


# This allows to get a fresh instance of a specific color:
# Color.white will return a NEW instance of Color('white')
for k, v in colors.items():
    __add_metacolor_property(k, v)


if __name__ == '__main__':
    red1 = Color('red')
    red2 = Color.red
    red3 = Color.red
    assert red1 != red2
    assert red2 != red3
    assert red1 != red3
    assert red1.r == red2.r == red3.r
