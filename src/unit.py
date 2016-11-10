import copy

from core.hex_lib import Hex, index_of_direction
import data_loader
from utils import attr, clamp
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

        self.skills = [RankedSkill(get_skill(n), Rank[rank]) for n, rank in data['skills'].items()] if 'skills' in data else []

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
        self.on_shield_change = Event()
        self.on_sim_move = Event('trajectory')
        self.on_skill_move = Event('context', 'unit')

    def __repr__(self):
        return 'U<{0}>'.format(self.template.name)

    def move_to(self, hex_coords=None, orientation=None):
        calc_shape = False
        if hex_coords and hex_coords != self.hex_coords:
            self.hex_coords = hex_coords
            calc_shape = True
        if orientation and orientation != self.orientation:
            self.orientation = orientation
            calc_shape = True
        if calc_shape:
            self.current_shape = self.calc_shape_at(self.hex_coords, self.orientation)

    def sim_move(self, trajectory):
        """ Move is ordered from simulation (AI, events...) and UI need to be aware
        UI must call move_to after"""
        self.on_sim_move(trajectory)

    def skill_move(self, context, unit=None):
        """ Skill move is not directly managed by the unit because UI may want to do something
        UI must call move_to after"""
        self.on_skill_move(context)

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
        return False

    def health_change(self, health, context):
        self.health = clamp(0, self.health + health, self.template.health)
        self.on_health_change(health, context)

    def shield_change(self, shield_index, context):
        self.shields[shield_index] -= 1
        self.on_shield_change()

    def get_shield(self, origin, destination):
        for shape_part_index, shape_part in enumerate(self.current_shape):
            if shape_part == destination:
                dir_index = index_of_direction(self.orientation)
                hit_index = index_of_direction(origin - destination)
                shield_index = shape_part_index * 6 + (6 - dir_index + hit_index) % 6
                if self.shields[shield_index] > 0:
                    return shield_index
        return -1


def load_all(root_path, get_skill):
    raw_units = data_loader.local_load(root_path + 'data/templates/units/', '.json')
    return [UnitTemplate(name, data, get_skill) for name, data in raw_units.items()]
