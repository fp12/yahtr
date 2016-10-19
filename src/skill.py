from enum import Enum

import data_loader
from core.hex_lib import Hex


class Effect(Enum):
    damage = 0
    heal = 1


class MoveCheck(Enum):
    none = 0  # should that even exist?
    goal_free = 1  # just making sure end point is not occupied


class MoveType(Enum):
    none = 0
    blink = 1
    pushed = 2


class HexDir:
    def __init__(self, data):
        q0, r0, q1, r1 = data
        self.origin = Hex(q=q0, r=r0)
        self.destination = Hex(q=q1, r=r1)
        self.angle = self.origin.angle_to_neighbour(self.destination - self.origin)

    def __repr__(self):
        return 'From {0} To {1}'.format(self.origin, self.destination)


class Hit:
    def __init__(self, data):
        self.direction = HexDir(data['dir']) if 'dir' in data else None
        self.effects = [Effect[e] for e in data['effects']] if 'effects' in data else []
        self.values = data.get('values', [])
        self.order = data['order'] if 'order' in data else 0


class UnitMove:
    def __init__(self, data):
        self.move = HexDir(data['move']) if 'move' in data else None
        self.orientation = HexDir(data['orientation']) if 'orientation' in data else None
        self.move_type = MoveType[data['type']] if 'type' in data else MoveType.none
        self.check = MoveCheck[data.get('check')] if 'check' in data else MoveCheck.none
        self.order = data['order'] if 'order' in data else 0


class HUN:
    def __init__(self, hun):
        self.hits = [Hit(h) for h in hun['H']] if 'H' in hun else []
        self.unit_move = UnitMove(hun['U']) if 'U' in hun else None
        self.ennemy_moves = [UnitMove(m) for m in hun['N']] if 'N' in hun else []

    @property
    def H(self):
        return self.hits

    @property
    def U(self):
        return self.unit_move

    @property
    def N(self):
        return self.ennemy_moves

    def __repr__(self):
        return 'Hits: {0}\n\tUnit move: {1}\n\tNMIs moves: {2}'.format(self.hits, self.unit_move, self.ennemy_moves)


class Skill:
    def __init__(self, name, data):
        self.name = name
        self.huns = [HUN(hun) for hun in data['HUN']] if 'HUN' in data else []

    def __repr__(self):
        return 'Sk<{0}>\n\t{1}'.format(self.name, '\n\t'.join(map(repr, self.huns)))


class RankedSkill:
    def __init__(self, skill, rank):
        self.skill = skill
        self.rank = rank

    def __repr__(self):
        return 'RkSk<{0}:{1}>'.format(self.skill.name, self.rank.name)

    def get_damage(self, hit):
        if Effect.damage in hit.effects:
            return hit.values[self.rank.value]
        return 0


def load_all(root_path):
    raw_skills = data_loader.local_load(root_path + 'data/skills/', '.json')
    return [Skill(name, data) for name, data in raw_skills.items()]
