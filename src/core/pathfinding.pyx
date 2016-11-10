from utils import PriorityQueue
from .hex_lib cimport Hex

cdef class Path:
    cdef frontier
    cdef Hex start
    cdef unsigned int max_cost
    cdef dict came_from
    cdef dict cost_so_far
    cdef object heuristic, get_neighbours, get_cost

    def __init__(self, Hex start, unsigned int max_cost, object heuristic, object get_neighbours, object get_cost):
        self.start = start
        self.max_cost = max_cost
        self.came_from = {start: None}
        self.cost_so_far = {start: 0}
        self.frontier = PriorityQueue()
        self.frontier.put(start, 0)
        self.heuristic, self.get_neighbours, self.get_cost = heuristic, get_neighbours, get_cost

    cdef list backtrack_path(self, Hex end):
        if end not in self.came_from:
            return []

        cdef list path = [end]
        cdef Hex backtrack_end = end
        while backtrack_end != self.start:
            backtrack_end = self.came_from[backtrack_end]
            path.append(backtrack_end)
        return path

    cpdef list get_best_to_goal(self, Hex goal):
        cdef Hex current
        cdef unsigned int new_cost, priority

        while not self.frontier.empty():
            current = self.frontier.get()
            if current == goal:
                break

            for neighbour in self.get_neighbours(current):
                new_cost = self.cost_so_far[current] + self.get_cost(neighbour)
                if new_cost <= self.max_cost and (neighbour not in self.cost_so_far or new_cost < self.cost_so_far[neighbour]):
                    self.cost_so_far[neighbour] = new_cost
                    priority = new_cost + self.heuristic(goal, neighbour)
                    self.frontier.put(neighbour, priority)
                    self.came_from[neighbour] = current

        return self.backtrack_path(goal)

    cdef list expand_shape(self, shape):
        cdef list shape_neighbours = []
        for h in shape:
            for neighbour in self.get_neighbours(h):
                if neighbour in shape_neighbours or neighbour in shape:
                    continue
                shape_neighbours.append(neighbour)
        return shape_neighbours

    cpdef list get_best_to_shape(self, list shape):
        cdef Hex current
        cdef unsigned int new_cost, priority
        cdef list expanded_shape = self.expand_shape(shape)

        while not self.frontier.empty():
            current = self.frontier.get()
            if current in expanded_shape or self.cost_so_far[current] == self.max_cost:
                break

            for neighbour in self.get_neighbours(current):
                expanded_shape_prio = PriorityQueue()
                for shape_part in expanded_shape:
                    expanded_shape_prio.put(shape_part, self.heuristic(shape_part, neighbour))

                while not expanded_shape_prio.empty():
                    heuristic, shape_part = expanded_shape_prio.get_with_priority()
                    new_cost = self.cost_so_far[current] + self.get_cost(neighbour)
                    if new_cost <= self.max_cost and (neighbour not in self.cost_so_far or new_cost < self.cost_so_far[neighbour]):
                        self.cost_so_far[neighbour] = new_cost
                        priority = new_cost + heuristic
                        self.frontier.put(neighbour, priority)
                        self.came_from[neighbour] = current
        else:
            print('get_best_to_shape - no best has been found?')

        return self.backtrack_path(current)


cdef class Reachable:
    cdef list openList, closedList
    cdef dict movementPoints
    cdef Hex start
    cdef object get_neighbours, get_cost
    cdef object sort_lambda

    def __init__(self, Hex start, unsigned int move_max, object get_neighbours, object get_cost):
        self.start = start
        self.openList = []
        self.closedList = []
        self.movementPoints = {start: move_max}
        self.get_neighbours = get_neighbours
        self.get_cost = get_cost
        self.sort_lambda = lambda h: self.movementPoints[h]

    cpdef list get(self):
        self.expand(self.start)
        cdef Hex next
        while len(self.openList) > 0:
            self.openList.sort(key=self.sort_lambda)
            next = self.openList.pop(-1)
            self.expand(next)

        self.closedList.remove(self.start)
        return self.closedList

    cdef void expand(self, h):
        cdef unsigned int parentPoints = self.movementPoints[h]
        cdef int points
        self.closedList.append(h)
        for neighbour in self.get_neighbours(h):
            if neighbour in self.closedList or neighbour in self.openList:
                continue
            points = parentPoints - self.get_cost(neighbour)
            if points < 0:
                continue  # hex is outside of the reachable area
            self.openList.append(neighbour)
            self.movementPoints[neighbour] = points
