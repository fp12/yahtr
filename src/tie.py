from enum import Enum


class Type(Enum):
    Neutral = 0
    Ally = 1
    Enemy = 2


class Tie:
    """ Relationship between two players """

    def __init__(self, p1, p2, tie_type):
        self.players = (p1, p2)
        self.tie_type = tie_type

    def has(self, p1, p2):
        return p1 in self.players and p2 in self.players
