import heapq
import itertools


class TimeBar:
    def __init__(self):
        self.queue = []
        self.count = itertools.count()
        self.callbacks = {'on_next': []}

    def __str__(self):
        return str(self.queue)

    def register_unit(self, unit):
        heapq.heappush(self.queue, (unit.initiative, next(self.count), unit))

    def register_units(self, units):
        for u in units:
            self.register_unit(u)

    def register_event(self, on_next=None):
        if on_next:
            self.callbacks['on_next'].append(on_next)

    @property
    def current(self):
        return self.queue[0]

    def next(self):
        old_priority, _, unit = heapq.heappop(self.queue)
        heapq.heappush(self.queue, (old_priority + unit.speed, next(self.count), unit))
        for cb in self.callbacks['on_next']:
            cb()
        return self.current

    def simulate_for(self, max_elements):
        copy = self.queue[:]
        index = 0
        count = itertools.count(start=next(self.count))
        while len(copy) < max_elements:
            copy = heapq.nsmallest(max_elements, copy)
            old_priority, _, unit = copy[index]
            heapq.heappush(copy, (old_priority + unit.speed, next(count), unit))
            index += 1
        return heapq.nsmallest(max_elements, copy)
