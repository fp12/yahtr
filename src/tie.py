from enum import Enum

from player import Player


class Type(Enum):
    Neutral = 0
    Ally = 1
    Enemy = 2


class Tie:
    def __init__(self, p1, p2, tie_type):
        self.players = (p1, p2)
        self.tie_type = tie_type

    def has(self, x1, x2):
        p1, p2 = x1, x2
        if not isinstance(x1, Player):
            p1 = x1.owner
        if not isinstance(x2, Player):
            p2 = x2.owner
        return p1 in self.players and p2 in self.players
