import copy

from hex_lib import Hex
import data_loader
from actions import ActionType, actions_trees
from rank import Rank
from skill import RankedSkill
from weapon import RankedWeapon


def copy_attr(a, b, *args):
    for arg in args:
        attr = getattr(a, arg)
        if isinstance(attr, list):
            setattr(b, arg, attr[:])
        else:
            setattr(b, arg, copy.copy(attr))


def get_attr_from_dic(a, data, *args):
        for arg in args:
            if arg in data:
                setattr(a, arg, data[arg])


class UnitTemplate:
    def __init__(self, name, data, get_skill):
        self.name = name
        get_attr_from_dic(self, data, 'move', 'initiative', 'speed', 'shields', 'color', 'weapons')
        self.actions_tree = actions_trees[data['actions_tree_name']]

        self.skills = []
        if 'skills' in data:
            self.skills = [RankedSkill(get_skill(n), Rank[rank]) for n, rank in data['skills'].items()]

        self.body = [Hex(0, 0)]
        if 'body' in data:
            self.body = []
            body_def = data['body']
            for index in range(0, len(body_def), 2):
                self.body.append(Hex(q=body_def[index], r=body_def[index + 1]))


class Unit:
    def __init__(self, template):
        self.template = template
        copy_attr(template, self, 'move', 'initiative', 'speed', 'shields', 'color', 'actions_tree', 'skills', 'body')
        self.hex_coords = None
        self.orientation = None
        self.equipped_weapons = []
        self.owner = None

    def __repr__(self):
        return 'U<{0}>'.format(self.template.name)

    def move_to(self, hex_coords=None, orientation=None):
        if hex_coords:
            self.hex_coords = hex_coords
        if orientation:
            self.orientation = orientation

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

    def calc_body_at(self, position, orientation):
        body = []
        for body_part in self.body:
            new_pos = copy.copy(body_part).rotate_to(orientation)
            new_pos += position
            body.append(new_pos)
        return body

    def hex_test(self, hex_coords):
        if hex_coords in self.calc_body_at(self.hex_coords, self.orientation):
            return True


def load_all(root_path, get_skill):
    raw_units = data_loader.local_load(root_path + 'data/templates/units/', '.json')
    return [UnitTemplate(name, data, get_skill) for name, data in raw_units.items()]
