import copy

from hex_lib import Hex
import data_loader
from utils import attr
from utils.event import Event
from actions import ActionType, actions_trees
from rank import Rank
from skill import RankedSkill
from weapon import RankedWeapon


class UnitTemplate:
    __attributes = ['move', 'initiative', 'speed', 'shields', 'color', 'weapons', 'health']

    def __init__(self, name, data, get_skill):
        self.name = name
        attr.get_from_dict(self, data, *UnitTemplate.__attributes)
        self.actions_tree = actions_trees[data['actions_tree_name']]

        self.skills = []
        if 'skills' in data:
            self.skills = [RankedSkill(get_skill(n), Rank[rank]) for n, rank in data['skills'].items()]

        self.shape = [Hex(0, 0)]
        if 'shape' in data:
            self.shape = []
            shape_def = data['shape']
            for index in range(0, len(shape_def), 2):
                self.shape.append(Hex(q=shape_def[index], r=shape_def[index + 1]))


class Unit:
    __attributes = ['move', 'initiative', 'speed', 'shields', 'color', 'actions_tree', 'skills', 'shape', 'health']

    def __init__(self, template):
        self.template = template
        attr.copy_from_instance(template, self, *Unit.__attributes)
        self.hex_coords = None
        self.orientation = None
        self.equipped_weapons = []
        self.owner = None
        self.current_shape = []
        if not self.shields:
            self.shields = [0 for _ in range(6)]

        # events
        self.on_health_change = Event('health', 'context')
        self.on_skill_move = Event('skill_move', 'unit')

    def __repr__(self):
        return 'U<{0}>'.format(self.template.name)

    def move_to(self, hex_coords=None, orientation=None):
        if hex_coords:
            self.hex_coords = hex_coords
        if orientation:
            self.orientation = orientation
        self.current_shape = self.calc_shape_at(self.hex_coords, self.orientation)

    def skill_move(self, unit_move, unit=None):
        """ Skill move is not directly managed by the unit because UI may want to do something
        UI must call move_to after"""
        self.on_skill_move(unit_move, unit)

    def equip(self, weapon):
        if weapon.wp_type.name in self.template.weapons:
            rank = Rank[self.template.weapons[weapon.wp_type.name]]
            self.equipped_weapons.append(RankedWeapon(weapon, rank))

    def get_skills(self, action_type):
        skills = []
        if action_type == ActionType.Weapon:
            for ranked_weapon in self.equipped_weapons:
                skills.extend(ranked_weapon.skills)
        elif action_type == ActionType.Skill:
            skills = self.skills
        return skills

    def calc_shape_at(self, position, orientation):
        shape = []
        for shape_part in self.shape:
            new_pos = copy.copy(shape_part).rotate_to(orientation)
            new_pos += position
            shape.append(new_pos)
        return shape

    def hex_test(self, hex_coords):
        if hex_coords in self.current_shape:
            return True

    def health_change(self, health, context):
        self.health += health
        self.on_health_change(health, context)


def load_all(root_path, get_skill):
    raw_units = data_loader.local_load(root_path + 'data/templates/units/', '.json')
    return [UnitTemplate(name, data, get_skill) for name, data in raw_units.items()]
