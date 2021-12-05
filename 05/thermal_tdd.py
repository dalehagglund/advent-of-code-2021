import unittest
import typing as ty

class Segment:
    x0: int
    y0: int
    x1: int
    y1: int
    def __init__(self, start, end):
        self.x0, self.y0 = start
        self.x1, self.y1 = end
    def point_track(self):
        dx = self._sign(self.x1 - self.x0)
        dy = self._sign(self.y1 - self.y0)
        x, y = self.x0, self.y0
        while True:
            yield (x, y)
            if (x, y) == (self.x1, self.y1):
                break
            x, y = x + dx, y + dy
    def _sign(self, x):
        if x < 0: return -1
        if x > 0: return +1
        return 0
class Map:
    _grid: ty.List[ty.List[int]]
    def __init__(self, nrow, ncol):
        self._grid = [ [ 0 ] * ncol for _ in range(ncol) ]
    def count_unsafe(self):
        return 0
    def count_at(self, x, y):
        return self._grid[x][y]
    def plot_track(self, seg: Segment):
        for x, y in seg. point_track():
            self._grid[x][y] += 1

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
    def testDownwardTwoPointTrack(self):
        seg =  Segment( (0, 0), (0, 1) )
        self.assertEqual(
            [ (0, 0), (0, 1) ],
            list(seg.point_track()))
    def testUpwardTwoPointTrack(self):
        seg =  Segment( (0, 1), (0, 0) )
        self.assertEqual(
            [ (0, 1), (0, 0) ],
            list(seg.point_track()))
    def testRightTrack(self):
        seg = Segment( (1, 1), (2, 1) )
        self.assertEqual(
            [ (1, 1), (2, 1) ],
            list(seg.point_track()))
    def testLeftTrack(self):
        seg = Segment( (2, 1), (1, 1) )
        self.assertEqual(
            [ (2, 1), (1, 1) ],
            list(seg.point_track()))

class TestMap(unittest.TestCase):
    def testEmptyMapHasNoIntersections(self):
        m = Map(10, 10)
        self.assertEqual(0, m.count_unsafe())
    def testCountsAreZeroWithEmptyMap(self):
        m = Map(10, 10)
        self.assertEqual(0,m.count_at(2, 2))
    def testCountSinglePointTrack(self):
        m = Map(10, 10)
        seg = Segment( (1, 1), (1, 1) )
        m.plot_track(seg)
        self.assertEqual(1, m.count_at(1, 1))
    def testHorizontalTrack(self):
        m = Map(10, 10)
        seg = Segment( (0, 1), (4, 1) )
        m.plot_track(seg)
        self.assertEqual(1, m.count_at(0, 1))
        self.assertEqual(1, m.count_at(4, 1))
