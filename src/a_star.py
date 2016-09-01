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


def heuristic(hex_a, hex_b):
    return hex_a.distance(hex_b)


def cost(hex_a, hex_b):
    return 1


def search(h_start, h_goal):
    frontier = PriorityQueue()
    frontier.put(h_start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[h_start] = None
    cost_so_far[h_start] = 0
    
    while not frontier.empty():
        h_current = frontier.get()
        
        if h_current == h_goal:
            break
        
        for h_next in h_current.get_neighbours():
            new_cost = cost_so_far[h_current] + cost(h_current, h_next)
            if h_next not in cost_so_far or new_cost < cost_so_far[h_next]:
                cost_so_far[h_next] = new_cost
                priority = new_cost + heuristic(h_goal, h_next)
                frontier.put(h_next, priority)
                came_from[h_next] = h_current
    
    return h_start, h_goal, came_from, cost_so_far

def build_path(h_start, h_goal, came_from, cost_so_far):
    path = [h_goal]
    backtrack_end = h_goal
    while backtrack_end != h_start:
        backtrack_end = came_from[backtrack_end]
        path.append(backtrack_end)
    return path
