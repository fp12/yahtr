import unittest

from core.hex_lib import Point, Hex, Layout


class TestPointCore(unittest.TestCase):
    def test_properties(self):
        p1 = Point(5, 2)
        self.assertEqual(p1.x, 5)
        self.assertEqual(p1.y, 2)

    def test_as_tuple(self):
        p1 = Point(5, 2)
        self.assertEqual(p1.tup, (5, 2))


class TestPointArithmetic(unittest.TestCase):
    def setUp(self):
        self.result = Point(4, -10)

    def test_add(self):
        p1 = Point(3, -7)
        p2 = Point(1, -3)
        result = p1 + p2
        self.assertEqual(result, self.result)

    def test_add_inplace(self):
        p1 = Point(3, -7)
        p1 += Point(1, -3)
        self.assertEqual(p1, self.result)

    def test_sub(self):
        p1 = Point(3, -7)
        p2 = Point(-1, 3)
        result = p1 - p2
        self.assertEqual(result, self.result)

    def test_sub_inplace(self):
        p1 = Point(3, -7)
        p1 -= Point(-1, 3)
        self.assertEqual(p1, self.result)


class TestHexCore(unittest.TestCase):
    def test_properties(self):
        h1 = Hex(5, 2)
        self.assertEqual(h1.q, 5)
        self.assertEqual(h1.r, 2)
        self.assertEqual(h1.s, -7)

    def test_length(self):
        h1 = Hex(2, 2)
        self.assertEqual(h1.length, 4)


class TestHexArithmetic(unittest.TestCase):
    def setUp(self):
        self.result = Hex(4, -10, 6)

    def test_add(self):
        h1 = Hex(3, -7, 4)
        h2 = Hex(1, -3, 2)
        result = h1 + h2
        self.assertEqual(result, self.result)

    def test_add_inplace(self):
        h1 = Hex(3, -7, 4)
        h1 += Hex(1, -3, 2)
        self.assertEqual(h1, self.result)

    def test_sub(self):
        h1 = Hex(3, -7, 4)
        h2 = Hex(-1, 3, -2)
        result = h1 - h2
        self.assertEqual(result, self.result)

    def test_sub_inplace(self):
        h1 = Hex(3, -7, 4)
        h1 -= Hex(-1, 3, -2)
        self.assertEqual(h1, self.result)


class TestLayoutCore(unittest.TestCase):
    def test_properties(self):
        l1 = Layout(origin=(12, 12), size=5, flat=True, margin=5)
        self.assertEqual(l1.origin, Point(12, 12))
        self.assertEqual(l1.size, Point(5, 5))
        self.assertEqual(l1.orientation.start_angle, 0)
        self.assertEqual(l1.margin, 5)


"""

def test_hex_direction():
    equal_hex("hex_direction", Hex(0, -1, 1), hex_direction(2))


def test_hex_neighbor():
    equal_hex("hex_neighbor", Hex(1, -3, 2), hex_neighbor(Hex(1, -2, 1), 2))


def test_hex_diagonal():
    equal_hex("hex_diagonal", Hex(-1, -1, 2), hex_diagonal_neighbor(Hex(1, -2, 1), 3))


def test_hex_distance():
    equal_int("hex_distance", 7, hex_distance(Hex(3, -7, 4), Hex(0, 0, 0)))


def test_hex_round():
    a = Hex(0, 0, 0)
    b = Hex(1, -1, 0)
    c = Hex(0, -1, 1)
    equal_hex("hex_round 1", Hex(5, -10, 5), hex_round(hex_lerp(Hex(0, 0, 0), Hex(10, -20, 10), 0.5)))
    equal_hex("hex_round 2", hex_round(a), hex_round(hex_lerp(a, b, 0.499)))
    equal_hex("hex_round 3", hex_round(b), hex_round(hex_lerp(a, b, 0.501)))
    equal_hex("hex_round 4", hex_round(a), hex_round(Hex(a.q * 0.4 + b.q * 0.3 + c.q * 0.3, a.r * 0.4 + b.r * 0.3 + c.r * 0.3, a.s * 0.4 + b.s * 0.3 + c.s * 0.3)))
    equal_hex("hex_round 5", hex_round(c), hex_round(Hex(a.q * 0.3 + b.q * 0.3 + c.q * 0.4, a.r * 0.3 + b.r * 0.3 + c.r * 0.4, a.s * 0.3 + b.s * 0.3 + c.s * 0.4)))


def test_layout():
    h = Hex(3, 4, -7)
    flat = Layout(layout_flat, Point(10, 15), Point(35, 71))
    equal_hex("layout", h, hex_round(pixel_to_hex(flat, hex_to_pixel(flat, h))))
    pointy = Layout(layout_pointy, Point(10, 15), Point(35, 71))
    equal_hex("layout", h, hex_round(pixel_to_hex(pointy, hex_to_pixel(pointy, h))))

"""

if __name__ == "__main__":
    unittest.main()
