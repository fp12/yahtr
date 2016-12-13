import unittest

from utils.attr import get_from_dict, copy_from_instance
from utils.color import Color


class Dummy:
    pass


class Test_Attr(unittest.TestCase):
    def setUp(self):
        self.dummy = Dummy()
        self.args = ['p1', 'p2', 'p3']
        self.d = {'p1': 'p1', 'p2': None, 'p4': {}}

    def test_get_from_dict(self):
        get_from_dict(self.dummy, self.d, *self.args)
        self.assertEqual(self.dummy.p1, 'p1')
        self.assertEqual(self.dummy.p2, None)
        self.assertEqual(self.dummy.p3, None)

    def test_copy_from_instance(self):
        dummy = Dummy()
        get_from_dict(dummy, self.d, *self.args)
        copy_from_instance(dummy, self.dummy, *self.args)
        self.assertEqual(self.dummy.p1, 'p1')
        self.assertEqual(self.dummy.p2, None)
        self.assertEqual(self.dummy.p3, None)


class Test_Color(unittest.TestCase):
    def test_core(self):
        self.assertEqual(Color.white.r, 1.)
        self.assertEqual(Color.white.g, 1.)
        self.assertEqual(Color.white.b, 1.)
        self.assertEqual(Color.white.a, 1.)
        self.assertEqual(Color.white.rgb, [1., 1., 1.])
        self.assertEqual(Color.white.rgb_dict, {'r': 1., 'g': 1., 'b': 1.})

    def test_access(self):
        red1 = Color('red')
        red2 = Color.red
        red3 = Color.red
        self.assertNotEqual(red1, red2)
        self.assertNotEqual(red2, red3)
        self.assertNotEqual(red1, red3)
        self.assertEqual(red1.r, red2.r)


if __name__ == "__main__":
    unittest.main()
