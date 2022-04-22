####
# File containing unittests for lamport clock class
#
#

# Dependencies
import unittest
# Local Dependencies
from lamport_clock import LamportClock



class TestLamportClockMethods(unittest.TestCase):
    def setUp(self):
        self.lc = LamportClock()

    def test_clock_increment(self):
        start = self.lc.get_time()
        self.lc.increment()
        end = self.lc.get_time()
        self.assertEqual(start + 1, end)

    def test_clock_update(self):
        self.lc.update(10)
        start = self.lc.get_time()
        self.assertEqual(start, 10)
        self.lc.increment()
        end = self.lc.get_time()
        self.assertEqual(end, 11)

    def tearDown(self):
        del self.lc

if __name__ == "__main__":
    unittest.main()
