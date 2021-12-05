import unittest
import typing as ty

class Map:
    _grid: ty.List[ty.List[int]]
    def __init__(self, nrow, ncol):
        self._grid = [ [ 0 ] * ncol for _ in range(ncol) ]
    def count_unsafe(self):
        return 0
    def count_at(self, x, y):
        return self._grid[x][y]
    def plot_track(self, seg: 'Segment'):
        for x, y in seg. point_track():
            self._grid[x][y] += 1

class Segment:
    x0: int
    y0: int
    x1: int
    y1: int
    def __init__(self, start, end):
        self.x0, self.y0 = start
        self.x1, self.y1 = end
    def point_track(self):
        yield (self.x0, self.y0)

class TestSegment(unittest.TestCase):
    def testInitialization(self):
        seg = Segment( (0, 2), (4, 6) )
        self.assertEqual(0, seg.x0)
        self.assertEqual(2, seg.y0)
        self.assertEqual(4, seg.x1)
        self.assertEqual(6, seg.y1)
    def testSinglePointSegment(self):
        seg = Segment( (0, 0), (0, 0) )
        track = list(seg.point_track())
        self.assertEqual( [ (0, 0) ], track )

class TestMap(unittest.TestCase):
    def testEmptyMapHasNoIntersections(self):
        m = Map(10, 10)
        self.assertEqual(0, m.count_unsafe())
    def testCountsAreZeroWithEmptyMap(self):
        m = Map(10, 10)
        self.assertEqual(0,m.count_at(2, 2))
    def testCountSinglePointTrack(self):
        m = Map(10, 10)
        seg = Segment( (1, 1), (1, 10) )
        m.plot_track(seg)
        self.assertEqual(1, m.count_at(1, 1))
