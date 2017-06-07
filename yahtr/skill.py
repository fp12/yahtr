from enum import Enum

from yahtr.data_loader import local_load
from yahtr.core.hex_lib import Hex
from yahtr.utils import attr


class Effect(Enum):
    none = 0
    hit_normal = 10
    hit_through_shield = 11
    hit_through_wall = 12
    hit_shield_only = 13
    hit_wall_only = 14
    heal = 20


class MoveCheck(Enum):
    none = 0  # should that even exist?
    goal_free = 1  # just making sure end point is not occupied


class MoveType(Enum):
    none = 0
    blink = 1
    pushed = 2


class Target:
    none = 0
    unit = 1
    shield = 2
    wall = 3


class HexDir:
    def __init__(self, data):
        q0, r0, q1, r1 = data
        self.origin = Hex(q=q0, r=r0)
        self.destination = Hex(q=q1, r=r1)
        self.angle = self.origin.angle_to_neighbour(self.destination - self.origin)

    def __repr__(self):
        return f'From {self.origin} To {self.destination}'


class Hit:
    def __init__(self, data):
        self.direction = HexDir(data['dir']) if 'dir' in data else None
        self.effects = [Effect[e] for e in data['effects']] if 'effects' in data else []
        self.values = data.get('values', [])
        self.order = data['order'] if 'order' in data else 0

    def valid_on_target(self, target):
        if target == Target.none:
            return False
        if target == Target.unit:
            return any(e in [Effect.hit_normal, Effect.hit_through_shield, Effect.hit_through_wall, Effect.heal] for e in self.effects)
        if target == Target.shield:
            return any(e in [Effect.hit_normal, Effect.hit_through_wall, Effect.hit_shield_only] for e in self.effects)
        if target == Target.wall:
            return any(e in [Effect.hit_normal, Effect.hit_through_shield, Effect.hit_wall_only] for e in self.effects)

    @property
    def is_damage(self):
        return any(e in [Effect.hit_normal,
                         Effect.hit_through_shield,
                         Effect.hit_through_wall,
                         Effect.hit_shield_only,
                         Effect.hit_wall_only] for e in self.effects)


class UnitMove:
    def __init__(self, data):
        self.move = HexDir(data['move']) if 'move' in data else None
        self.orientation = HexDir(data['orientation']) if 'orientation' in data else None
        self.move_type = MoveType[data['type']] if 'type' in data else MoveType.none
        self.check = MoveCheck[data.get('check')] if 'check' in data else MoveCheck.none
        self.order = data['order'] if 'order' in data else 0


class HUN:
    """ Hit - Unit - eNmeny data format for skills """

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
        return f'Hits: {self.hits}\n\tUnit move: {self.unit_move}\n\tNMIs moves: {self.ennemy_moves}'


class Skill:
    """ Skill as defined in data """

    __attributes = ['name', 'description']

    def __init__(self, file, data):
        self.id = file
        attr.get_from_dict(self, data, *Skill.__attributes)
        self.huns = [HUN(hun) for hun in data['HUN']] if 'HUN' in data else []

    def __repr__(self):
        return 'Sk<{0}>\n\t{1}'.format(self.name, '\n\t'.join(map(repr, self.huns)))


class RankedSkill:
    """ Skill instanciated inside a weapon or a unit """

    def __init__(self, skill, rank):
        self.skill = skill
        self.rank = rank

    def __repr__(self):
        return f'RkSk<{self.skill.name}:{self.rank.name}>'

    def hit_value(self, hit):
        return hit.values[self.rank.value]


def load_all():
    raw_skills = local_load('data/skills/', '.json')
    return [Skill(file, data) for file, data in raw_skills.items()]
