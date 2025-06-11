import unittest
from main import get_aspect_ratio

class DummyLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TestPipeface(unittest.TestCase):
    def test_get_aspect_ratio(self):
        top = DummyLandmark(0, 0)
        bottom = DummyLandmark(0, 2)
        right = DummyLandmark(2, 0)
        left = DummyLandmark(0, 0)
        ratio = get_aspect_ratio(top, bottom, right, left)
        self.assertEqual(ratio, 1.0)

if __name__ == '__main__':
    unittest.main()