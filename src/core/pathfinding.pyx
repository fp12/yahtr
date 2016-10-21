from utils import PriorityQueue
from .hex_lib cimport Hex


cpdef list get_best_path(Hex start, Hex goal, heuristic, get_neighbours, get_cost):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    cdef dict came_from = {}
    cdef dict cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    cdef Hex current
    cdef unsigned int new_cost, priority

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for neighbour in get_neighbours(current):
            new_cost = cost_so_far[current] + get_cost(neighbour)
            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                priority = new_cost + heuristic(goal, neighbour)
                frontier.put(neighbour, priority)
                came_from[neighbour] = current

    # Maybe the goal was behind a wall...
    # it can happen, so no real error notification
    if goal not in came_from:
        return []

    cdef list path = [goal]
    cdef Hex backtrack_end = goal
    while backtrack_end != start:
        backtrack_end = came_from[backtrack_end]
        path.append(backtrack_end)
    return path


cdef class Reachable:
    cdef list openList, closedList
    cdef dict movementPoints
    cdef Hex start
    cdef object get_neighbours, get_cost
    cdef object sort_lambda

    def __init__(self, Hex start, unsigned int move_max, get_neighbours, get_cost):
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
