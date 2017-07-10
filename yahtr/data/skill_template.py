from enum import Enum

from yahtr.data.core import DataTemplate
from yahtr.localization.core import LocStr
from yahtr.core.hex_lib import HexDir
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

    goal_free = 10  # just making sure end point is not occupied
    goal_hole = 11  # what could I do with that?
    goal_teammate = 12  # a teammate unit is on the end point
    goal_ennemy = 13  # an ennemy unit is on the end point

    trajectory_free = 20  # trajectory is on normal tiles
    trajectory_hole = 21  # trajectory is on holes
    trajectory_ally = 22  # jumping over ally
    trajectory_ennemy = 23  # jumping over ennemies


class MoveType(Enum):
    none = 0
    blink = 1
    pushed = 2
    jump_over_tile = 3
    jump_over_ally = 4


class Target(Enum):
    none = 0
    unit = 1
    shield = 2
    wall = 3


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

    def __repr__(self):
        return f'{" ".join([e.name for e in self.effects])}'


class UnitMove:
    def __init__(self, data):
        self.move = HexDir(data['move']) if 'move' in data else None
        self.orientation = HexDir(data['orientation']) if 'orientation' in data else None
        self.move_type = MoveType[data['type']] if 'type' in data else MoveType.none
        self.check = [MoveCheck[c] for c in data['check']] if 'check' in data else []
        self.order = data['order'] if 'order' in data else 0


class HUN:
    """ Hit - Unit - eNneny data format for skills """

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


class SkillTemplate(DataTemplate):
    """ Skill as defined in data """

    __path = 'data/skills/'
    __ext = '.json'

    __attributes = []

    def __init__(self, file_id, data, **kwargs):
        super(SkillTemplate, self).__init__(file_id, **kwargs)
        attr.get_from_dict(self, data, *SkillTemplate.__attributes)
        self.huns = [HUN(hun) for hun in data['HUN']] if 'HUN' in data else []
        self.name = LocStr(self.loc_key_name)
        self.description = LocStr(self.loc_key_desc)

    def __repr__(self):
        return 'Sk<{0!s}>\n\t{1}'.format(self.name, '\n\t'.join(map(repr, self.huns)))

    @property
    def loc_key_name(self):
        return 'L_SKILL_NAME/{0}'.format(self.file_id.replace('\\', '/'))

    @property
    def loc_key_desc(self):
        return 'L_SKILL_DESC/{0}'.format(self.file_id.replace('\\', '/'))

    @staticmethod
    def load_all(**kwargs):
        raw_skills = DataTemplate.local_load(SkillTemplate.__path, SkillTemplate.__ext)
        return [SkillTemplate(file, data, **kwargs) for file, data in raw_skills.items()]

    @staticmethod
    def load_one(skill_id, **kwargs):
        data = DataTemplate.local_load_single(SkillTemplate.__path, skill_id, SkillTemplate.__ext)
        if data:
            return SkillTemplate(skill_id, data, **kwargs)
        return None
