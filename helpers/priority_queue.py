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

    def remove_by_id(self, process_id):
        index = -1
        for it in range(len(self.pq)):
            if self.pq[it][1] == process_id:
                index = it
                break
        if index != -1:
            self.pq.pop(index)
        heapq.heapify(self.pq)

    def get_head(self):
        return self.pq[0]

    def get_queue(self):
        return self.pq


