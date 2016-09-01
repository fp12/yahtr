from math import sqrt, pi, cos, sin
import collections


_SQRT3 = sqrt(3)
_SQRT3div2 = _SQRT3 / 2.0
_SQRT3div3 = _SQRT3 / 3.0
_2PIdiv6 = 2.0 * pi / 6.0


class Hex:
    directions = [(0, 1, -1), (1, 0, -1), (1, -1, 0), (0, -1, 1), (-1, 0, 1), (-1, 1, 0)]
    angles = [0, -60, -120, -180, -240, -300]

    def __init__(self, q=0, r=0, s=0, qrs=()):
        if qrs and len(qrs) >= 2:
            self._q = qrs[0]
            self._r = qrs[1]
        else:
            self._q = q
            self._r = r

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
        return '<{0}, {1}, {2}>'.format(self._q, self._r, self.s)

    def __repr__(self):
        return '<{0}, {1}, {2}>'.format(self._q, self._r, self.s)

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

    def angle_to_neighbour(self, other):
        neighbour = other - self
        if neighbour in Hex.directions:
            return Hex.angles[Hex.directions.index(neighbour)]
        return 0

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
            else:
                s = -q - r
        return Hex(q, r, s)


Point = collections.namedtuple("Point", ["x", "y"])


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

    def hex_corner_offset(self, corner):
        angle = (self._orientation.start_angle - corner) * _2PIdiv6
        return Point(self._size.x * cos(angle), self._size.y * sin(angle))

    def polygon_corners(self, h):
        corners = []
        center = self.hex_to_pixel(h)
        for i in range(0, 6):
            offset = self.hex_corner_offset(i)
            corners.append(Point(center.x + offset.x, center.y + offset.y))
        return corners

    def get_mid_edge_position(self, h1, h2):
        c1 = self.hex_to_pixel(h1)
        c2 = self.hex_to_pixel(h2)
        return Point(c1.x + (c2.x - c1.x) / 2, c1.y + (c2.y - c1.y) / 2)
