from .priority_queue import PriorityQueue, EqualPriorityQueue
from .color import Color


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))
