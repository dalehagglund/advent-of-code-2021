import unittest

class Map:
    def count_unsafe(self):
        return 0

class TestMap(unittest.TestCase):
    def testEmptyMapHasNoIntersections(self):
        m = Map()
        self.assertAlmostEquals(0, m.count_unsafe())