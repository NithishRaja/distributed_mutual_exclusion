####
# Unittests for priority queue class
#
#

# Dependencies
import unittest, heapq
# Local Dependencies
from priority_queue import PriorityQueue

class TestPriorityQueueMethods(unittest.TestCase):
    def setUp(self):
        self.pq = PriorityQueue()

    def test_insert(self):
        for it in range(5):
            self.pq.insert(it*10, it)
        queue = self.pq.get_queue()
        for it in range(5):
            self.assertEqual(queue[it][0], it*10)
            self.assertEqual(queue[it][1], it)

    def test_sorted_property(self):
        for it in range(5):
            self.pq.insert(10 - it, it)
        queue = self.pq.get_queue()
        for it in range(5):
            elem = heapq.heappop(queue)
            self.assertEqual(elem[0], it + 6)
            self.assertEqual(elem[1], 4 - it)

    def test_tie_breaks(self):
        for it in range(5):
            self.pq.insert(10, 10 - it)
        queue = self.pq.get_queue()
        for it in range(5):
            elem = heapq.heappop(queue)
            self.assertEqual(elem[0], 10)
            self.assertEqual(elem[1], it + 6)

    def test_remove(self):
        for it in range(5):
            self.pq.insert(it*10, it)
        self.pq.remove_by_id(1)
        queue = self.pq.get_queue()
        for it in range(len(queue)):
            self.assertNotEqual(queue[it][0], 1*10)
            self.assertNotEqual(queue[it][1], 1)

    def TearDown(self):
        del self.pq

if __name__ == "__main__":
    unittest.main()
