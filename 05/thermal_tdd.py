import unittest

class Map:
    def __init__(self, nrow, ncol):
        pass
    def count_unsafe(self):
        return 0
    def count_at(self, x, y):
        return 0

class TestMap(unittest.TestCase):
    def testEmptyMapHasNoIntersections(self):
        m = Map(10, 10)
        self.assertAlmostEquals(0, m.count_unsafe())
    def testCountsAreZeroWithEmptyMap(self):
        m = Map(10, 10)
        self.assertEquals(0,m.count_at(2, 2))