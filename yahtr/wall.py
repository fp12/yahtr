from enum import Enum

from core.hex_lib import Hex


class WallType(Enum):
    breakable = 1


class Wall:
    """ Class representing a wall on the game board
    Its data format is a simple list:
    [origin.q, origin.r, destination.q, destination.r, type_0, type_1, ..., type_n]
    Note: A wall can have no type
    """

    def __init__(self, data):
        self.origin = Hex(*data[0:2])
        self.destination = Hex(*data[2:4])
        self.types = [WallType(x) for x in data[4:]]

    def __eq__(self, other):
        if isinstance(other, Wall):
            return other.origin == self.origin and other.destination == self.destination
        o1, o2 = other
        return (o1 == self.origin and o2 == self.destination) or (o1 == self.destination and o2 == self.origin)
