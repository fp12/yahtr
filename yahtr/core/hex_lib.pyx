#cython: language_level=3

from libc.math cimport pi, sin, cos, sqrt


DEF NHEX = 6


cdef int directions[NHEX][2]
directions = [[0, 1], [1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1]]
cdef int angles[NHEX]
angles = [0, -60, -120, -180, -240, -300]

cpdef short index_of_direction(Hex direction):
    cdef short i
    for i in range(NHEX):
        if directions[i][0] == direction.q and directions[i][1] == direction.r:
            return i
    return -1


cpdef int hex_angle(short i):
    return angles[i]


cpdef Hex get_hex_direction(short i):
    return Hex(directions[i][0], directions[i][1])


cdef class Hex:
    def __cinit__(self, int q, int r, int s = 0):
        self.q, self.r = q, r
        self.neighbours = []

    @property
    def s(self):
        return -self.q - self.r

    @property
    def length(self):
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def __str__(self):
        return 'H<{0}, {1}, {2}>'.format(self.q, self.r, self.s)

    def __repr__(self):
        return 'H<{0}, {1}, {2}>'.format(self.q, self.r, self.s)

    def __hash__(self):
        return hash(str(self))

    def __richcmp__(Hex first, other, int op):
        if other:
            other = other if isinstance(other, Hex) else Hex(other[0], other[1])
        if op == 0:  # <
            return not other or first.q < other.q or first.r < other.r
        elif op == 1:  # <=
            return other and first.q <= other.q and first.r <= other.r
        elif op == 2:  # ==
            return other and first.q == other.q and first.r == other.r
        elif op == 3:  # !=
            return not other or first.q != other.q or first.r != other.r
        elif op == 4:  # >
            return not other or first.q > other.q or first.r > other.r
        elif op == 5:  # >=
            return other and first.q >= other.q and first.r >= other.r

    def __add__(Hex first, Hex second):
        return Hex(first.q + second.q, first.r + second.r)

    def __iadd__(self, Hex other):
        self.q += other.q
        self.r += other.r
        return self

    def __sub__(Hex first, Hex second):
        return Hex(first.q - second.q, first.r - second.r)

    def __isub__(self, Hex other):
        self.q -= other.q
        self.r -= other.r
        return self

    def __reduce__(self):
        # needed for copy and deepcopy:
        # a tuple as specified in the pickle docs - (class_or_constructor, (tuple, of, args, to, constructor))
        return (self.__class__, (self.q, self.r))

    cpdef int distance(self, Hex other):
        return (self - other).length

    cpdef list get_neighbours(self):
        if len(self.neighbours) == 0:
            self.neighbours = [self + Hex(x[0], x[1]) for x in directions]
        return self.neighbours

    cpdef Hex get_neighbour(self, size_t direction):
        return self + Hex(directions[direction][0], directions[direction][1])

    cpdef int angle_to_neighbour(self, Hex neighbour):
        cdef short i = index_of_direction(neighbour)
        return hex_angle(i) if 0 <= i < NHEX else 0

    cpdef Hex rotate_to(self, Hex direction):
        cdef short i = index_of_direction(direction)
        if 0 <= i < NHEX:
            for __ in range(i):
                q, s = self.q, -self.q - self.r
                self.q = -s
                self.r = -q
        return self

    cpdef Hex direction_to_distant(self, Hex other):
        cdef double step = 1. / max(self.distance(other), 1.)
        cdef double q = self.q * (1. - step) + other.q * step
        cdef double r = self.r * (1. - step) + other.r * step
        return Hex.get_round(q, r) - self

    @staticmethod
    cdef Hex get_round(double fq, double fr):
        cdef double fs = -fq - fr
        cdef int q = int(round(fq))
        cdef int r = int(round(fr))
        cdef int s = int(round(fs))
        cdef double q_diff = abs(q - fq)
        cdef double r_diff = abs(r - fr)
        cdef double s_diff = abs(s - fs)
        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        else:
            if r_diff > s_diff:
                r = -q - s
        return Hex(q, r)


cdef class Point:
    cdef readonly double x, y

    def __cinit__(self, double x, double y):
        self.x, self.y = x, y

    @property
    def tup(self):
        return (self.x, self.y)

    def __str__(self):
        return 'P<{0}, {1}>'.format(self.x, self.y)

    def __repr__(self):
        return 'P<{0}, {1}>'.format(self.x, self.y)

    def __hash__(self):
        return hash(str(self))

    def __richcmp__(Point first, other, int op):
        if other:
            other = other if isinstance(other, Point) else Point(*other)
        if op == 0:  # <
            return not other or first.x < other.x or first.y < other.y
        elif op == 1: # <=
            return other and first.x <= other.x and first.y <= other.y
        elif op == 2:  # ==
            return other and first.x == other.x and first.y == other.y
        elif op == 3:  # !=
            return not other or first.x != other.x or first.y != other.y
        elif op == 4:  # >
            return not other or first.x > other.x or first.y > other.y
        elif op == 5:  # >=
            return other and first.x >= other.x and first.y >= other.y

    def __add__(first, second):
        second = second if isinstance(second, Point) else Point(*second)
        return Point(first.x + second.x, first.y + second.y)

    def __iadd__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(first, second):
        second = second if isinstance(second, Point) else Point(*second)
        return Point(first.x - second.x, first.y - second.y)

    def __isub__(self, other):
        other = other if isinstance(other, Point) else Point(*other)
        self.x -= other.x
        self.y -= other.y
        return self

    def __reduce__(self):
        # needed for copy and deepcopy:
        # a tuple as specified in the pickle docs - (class_or_constructor, (tuple, of, args, to, constructor))
        return (self.__class__, (self.x, self.y))


cdef Point to_point(x):
    return x if isinstance(x, Point) else Point(x[0], x[1])


cdef class Orientation:
    cdef readonly double f0, f1, f2, f3, f4, b0, b1, b2, b3
    cdef readonly double start_angle

    def __cinit__(self, double f0, double f1, double f2, double f3, double b0, double b1, double b2, double b3, double start_angle):
        self.f0, self.f1, self.f2, self.f3 = f0, f1, f2, f3
        self.b0, self.b1, self.b2, self.b3 = b0, b1, b2, b3
        self.start_angle = start_angle


cdef double _SQRT3 = sqrt(3.)
cdef double _SQRT3div2 = _SQRT3 / 2.
cdef double _SQRT3div3 = _SQRT3 / 3.
cdef double _2PIdiv6 = 2. * pi / 6.
cdef Orientation pointy_orientation = Orientation(_SQRT3, _SQRT3div2, 0., 3. / 2., _SQRT3div3, -1. / 3., 0., 2. / 3., 0.5)
cdef Orientation flat_orientation = Orientation(3. / 2., 0., _SQRT3div2, _SQRT3, 2. / 3., 0., -1. / 3., _SQRT3div3, 0.)


cdef class Layout:
    cdef readonly Point origin, size
    cdef readonly Orientation orientation
    cdef readonly double margin

    def __cinit__(self, origin, size, bint flat=True, double margin=0.):
        self.origin = to_point(origin)
        self.size = size if type(size) == Point else Point(size, size)
        self.orientation = flat_orientation if flat else pointy_orientation
        self.margin = margin

    cpdef Point hex_to_pixel(self, Hex h):
        cdef double x = (self.orientation.f0 * h.q + self.orientation.f1 * h.r) * (self.size.x + self.margin)
        cdef double y = (self.orientation.f2 * h.q + self.orientation.f3 * h.r) * (self.size.y + self.margin)
        return Point(x + self.origin.x, y + self.origin.y)

    cpdef Hex pixel_to_hex(self, p):
        cdef Point pt = to_point(p)
        pt = Point((pt.x - self.origin.x) / (self.size.x + self.margin), (pt.y - self.origin.y) / (self.size.y + self.margin))
        cdef double q = self.orientation.b0 * pt.x + self.orientation.b1 * pt.y
        cdef double r = self.orientation.b2 * pt.x + self.orientation.b3 * pt.y
        return Hex.get_round(q, r)

    cpdef Point hex_corner_offset(self, int corner, bint add_margin=False):
        cdef double angle = (self.orientation.start_angle - corner) * _2PIdiv6
        cdef double size_x = self.size.x + (self.margin if add_margin else 0.)
        cdef double size_y = self.size.y + (self.margin if add_margin else 0.)
        return Point(size_x * cos(angle), size_y * sin(angle))

    cpdef list polygon_corners(self, Hex h, bint add_margin=False):
        corners = []
        cdef Point center = self.hex_to_pixel(h)
        cdef Point offset
        cdef short i
        for i in range(NHEX):
            offset = self.hex_corner_offset(i, add_margin)
            corners.append(Point(center.x + offset.x, center.y + offset.y))
        return corners

    cpdef Point get_mid_edge_position(self, Hex h1, Hex h2):
        cdef Point c1 = self.hex_to_pixel(h1)
        cdef Point c2 = self.hex_to_pixel(h2)
        return Point(c1.x + (c2.x - c1.x) / 2., c1.y + (c2.y - c1.y) / 2.)
