from math import sqrt, pi, cos, sin
import collections


_SQRT3 = sqrt(3)
_SQRT3div2 = _SQRT3 / 2.0
_SQRT3div3 = _SQRT3 / 3.0
_2PIdiv6 = 2.0 * pi / 6.0


class Hex:
    directions = [(0, 1, -1), (1, 0, -1), (1, -1, 0), (0, -1, 1), (-1, 0, 1), (-1, 1, 0)]
    angles = [0, -60, -120, -180, -240, -300]

    def __init__(self, q=0, r=0, qrs=()):
        if qrs and len(qrs) >= 2:
            self._q, self._r = qrs[0:2]
        else:
            self._q, self._r = q, r

    @property
    def q(self):
        return self._q

    @property
    def r(self):
        return self._r

    @property
    def s(self):
        return -self._q - self._r

    @property
    def length(self):
        return (abs(self._q) + abs(self._r) + abs(self.s)) // 2

    def __str__(self):
        return 'H<{0}, {1}, {2}>'.format(self._q, self._r, self.s)

    def __repr__(self):
        return 'H<{0}, {1}, {2}>'.format(self._q, self._r, self.s)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        other = other if type(other) is Hex else Hex(qrs=other)
        return self._q == other.q and self._r == other.r

    def __lt__(self, other):
        return self._q < other.q or self._r < other.r

    def __add__(self, other):
        return Hex(self._q + other.q, self._r + other.r)

    def __iadd__(self, other):
        self._q += other.q
        self._r += other.r
        return self

    def __sub__(self, other):
        return Hex(self._q - other.q, self._r - other.r)

    def __isub__(self, other):
        self._q -= other.q
        self._r -= other.r
        return self

    def __mul__(self, scale):
        return Hex(self._q * scale, self._r * scale)

    def __imul__(self, scale):
        self._q *= scale
        self._r *= scale
        return self

    def distance(self, other):
        return (self - other).length

    def get_neighbours(self):
        return [self + Hex(qrs=x) for x in Hex.directions]

    def get_neighbour(self, direction):
        return self + Hex(qrs=Hex.directions[direction])

    def angle_to_neighbour(self, neighbour):
        if neighbour in Hex.directions:
            return Hex.angles[Hex.directions.index(neighbour)]
        return 0

    def rotate_to(self, direction):
        index = Hex.directions.index(direction)
        for _ in range(index):
            q, s = self._q, -self._q - self._r
            self._q = -s
            self._r = -q
        return self

    def direction_to_distant(self, other):
        step = 1.0 / max(self.distance(other), 1)
        direction = Hex(q=self._q * (1 - step) + other.q * step, r=self._r * (1 - step) + other.r * step).get_round()
        direction -= self
        assert (direction in Hex.directions), '{} to {} = {}'.format(self, other, direction)
        return direction

    def get_round(self):
        q = int(round(self._q))
        r = int(round(self._r))
        s = int(round(self.s))
        q_diff = abs(q - self._q)
        r_diff = abs(r - self._r)
        s_diff = abs(s - self.s)
        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        else:
            if r_diff > s_diff:
                r = -q - s
        return Hex(q, r)


class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def tup(self):
        return (self._x, self._y)

    def __str__(self):
        return 'P<{0}, {1}>'.format(self._x, self._y)

    def __repr__(self):
        return 'P<{0}, {1}>'.format(self._x, self._y)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        return self._x == other.x and self._y == other.y

    def __add__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        return Point(self._x + other.x, self._y + other.y)

    def __iadd__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        self._x += other.x
        self._y += other.y
        return self

    def __sub__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        return Point(self._x - other.x, self._y - other.y)

    def __isub__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        self._x -= other.x
        self._y -= other.y
        return self


def to_point(x):
    return x if type(x) == Point else Point(x[0], x[1])


class Layout:
    Orientation = collections.namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])
    Pointy = Orientation(_SQRT3, _SQRT3div2, 0.0, 3 / 2, _SQRT3div3, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
    Flat = Orientation(3.0 / 2.0, 0.0, _SQRT3div2, _SQRT3, 2.0 / 3.0, 0.0, -1.0 / 3.0, _SQRT3div3, 0.0)

    def __init__(self, origin, size, flat=True, margin=0):
        self._origin = to_point(origin)
        self._size = size if type(size) == Point else Point(size, size)
        self._orientation = Layout.Flat if flat else Layout.Pointy
        self._margin = margin

    @property
    def origin(self):
        return self._origin

    @property
    def size(self):
        return self._size

    @property
    def orientation(self):
        return self._orientation

    @property
    def margin(self):
        return self._margin

    def hex_to_pixel(self, h):
        x = (self._orientation.f0 * h.q + self._orientation.f1 * h.r) * (self._size.x + self._margin)
        y = (self._orientation.f2 * h.q + self._orientation.f3 * h.r) * (self._size.y + self._margin)
        return Point(x + self._origin.x, y + self._origin.y)

    def pixel_to_hex(self, p):
        p = to_point(p)
        pt = Point((p.x - self._origin.x) / (self._size.x + self._margin), (p.y - self._origin.y) / (self._size.y + self._margin))
        q = self._orientation.b0 * pt.x + self._orientation.b1 * pt.y
        r = self._orientation.b2 * pt.x + self._orientation.b3 * pt.y
        return Hex(q, r)

    def hex_corner_offset(self, corner, add_margin=False):
        angle = (self._orientation.start_angle - corner) * _2PIdiv6
        size_x = self._size.x + self._margin if add_margin else 0
        size_y = self._size.y + self._margin if add_margin else 0
        return Point(size_x * cos(angle), size_y * sin(angle))

    def polygon_corners(self, h, add_margin=False):
        corners = []
        center = self.hex_to_pixel(h)
        for i in range(6):
            offset = self.hex_corner_offset(i, add_margin)
            corners.append(Point(center.x + offset.x, center.y + offset.y))
        return corners

    def get_mid_edge_position(self, h1, h2):
        c1 = self.hex_to_pixel(h1)
        c2 = self.hex_to_pixel(h2)
        return Point(c1.x + (c2.x - c1.x) / 2, c1.y + (c2.y - c1.y) / 2)