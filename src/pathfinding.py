import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def get_best_path(start, goal, heuristic, get_neighbours, get_cost):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

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
    backtrack_end = goal
    while backtrack_end != start:
        backtrack_end = came_from[backtrack_end]
        path.append(backtrack_end)
    return path


def get_reachable_simple(start, move_max, get_neighbours):
    visited = set([start])
    fringes = [[start]]

    for k in range(1, move_max + 1):
        fringes.append([])
        for h_current in fringes[k - 1]:
            for neighbour in get_neighbours(h_current):
                if neighbour not in visited:
                    visited.add(neighbour)
                    fringes[k].append(neighbour)
    visited.remove(start)
    return visited


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
