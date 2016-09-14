import copy

import data_loader
from actions import ActionType, actions_trees
from rank import Rank
from skill import RankedSkill
from weapon import RankedWeapon


class UnitTemplate:
    def __init__(self, name, data, get_skill):
        self.name = name
        self.auto_get(data, 'move', 'initiative', 'speed', 'shields', 'color', 'weapons')
        self.actions_tree = actions_trees[data['actions_tree_name']]
        self.skills = []
        if 'skills' in data:
            self.skills = [RankedSkill(get_skill(n), Rank[rank]) for n, rank in data['skills'].items()]

    def auto_get(self, data, *args):
        for arg in args:
            if arg in data:
                setattr(self, arg, data[arg])


def copy_attr(a, b, *args):
    for arg in args:
        attr = getattr(a, arg)
        if isinstance(attr, list):
            setattr(b, arg, attr[:])
        else:
            setattr(b, arg, copy.copy(attr))


class Unit:
    def __init__(self, template):
        self.template = template
        copy_attr(template, self, 'move', 'initiative', 'speed', 'shields', 'color', 'actions_tree', 'skills')
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


def load_all(root_path, get_skill):
    raw_units = data_loader.local_load(root_path + 'data/templates/units/', '.json')
    return [UnitTemplate(name, data, get_skill) for name, data in raw_units.items()]
