import heapq
import itertools


class TimeBar:
    def __init__(self):
        self.queue = []
        self.count = itertools.count()

    def __str__(self):
        return str(self.queue)

    def register_unit(self, unit):
        heapq.heappush(self.queue, (unit.template['initiative'], next(self.count), unit))

    def register_units(self, units):
        for u in units:
            self.register_unit(u)

    @property
    def current(self):
        return self.queue[0]

    def next(self):
        first = heapq.heappop(self.queue)
        new = (first[0] + first[2].template['speed'], next(self.count), first[2])
        heapq.heappush(self.queue, new)
        return self.current

    def simulate_for(self):
        max_ = 10
        copy = self.queue[:]
        index = 0
        count = itertools.count(start=next(self.count))
        while len(copy) < max_:
            current = copy[index]
            heapq.heappush(copy, (current[0] + current[2].template['speed'], next(count), current[2]))
            index += 1
        return copy
