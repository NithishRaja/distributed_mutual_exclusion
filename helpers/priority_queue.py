####
# Implementation of priority queue
#
#

# Dependencies
import heapq

class PriorityQueue:
    def __init__(self):
        self.pq = []

    def insert(self, timestamp, process_id):
        heapq.heappush(self.pq, (timestamp, process_id))

    def remove(self):
        heapq.heappop(self.pq)

    def get_head(self):
        return self.pq[0]

    def get_queue(self):
        return self.pq


