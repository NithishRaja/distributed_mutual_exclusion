####
# Implementation of lamport clock
#
#

# Dependencies

class LamportClock:
    def __init__(self):
        self.timer = 0

    def increment(self):
        self.timer = self.timer + 1

    def update(self, val):
        self.timer = val

    def get_time(self):
        return self.timer
