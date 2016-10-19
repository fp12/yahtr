from utils import PriorityQueue
from .hex_lib cimport Hex


cpdef get_best_path(Hex start, Hex goal, heuristic, get_neighbours, get_cost):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    cdef dict came_from = {}
    cdef dict cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    cdef Hex current
    cdef int new_cost, priority

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

    # something wrong happened?!
    if goal not in came_from:
        return []

    path = [goal]
    cdef Hex backtrack_end = goal
    while backtrack_end != start:
        backtrack_end = came_from[backtrack_end]
        path.append(backtrack_end)
    return path


def get_reachable(start, move_max, get_neighbours, get_cost):
    def expand(h):
        parentPoints = movementPoints[h]
        closedList.append(h)
        for neighbour in get_neighbours(h):
            if neighbour in closedList or neighbour in openList:
                continue
            points = parentPoints - get_cost(neighbour)
            if points < 0:
                continue  # hex is outside of the reachable area
            openList.append(neighbour)
            movementPoints[neighbour] = points

    openList = []
    closedList = []
    movementPoints = {start: move_max}

    expand(start)

    while len(openList) > 0:
        openList.sort(key=lambda h: movementPoints[h])
        h = openList.pop(-1)
        expand(h)

    return closedList
