from enum import Enum

import data_loader
from skill import RankedSkill


class Type(Enum):
    sword = 1
    daggers = 2
    spear = 3
    scythe = 4
    grimoire = 5


class WeaponTemplate:
    """ Weapon as defined in data"""
    def __init__(self, name, data, get_skill):
        self.name = name
        self.wp_type = Type[data['type']]
        self.skills = []
        if 'skills' in data:
            self.skills = [get_skill(s) for s in data['skills']]

    def __repr__(self):
        return 'WpTp<{0}>'.format(self.name)


class Weapon:
    """ Weapon instance that a player is holding """
    def __init__(self, wp_template):
        self.template = wp_template

    @property
    def wp_type(self):
        return self.template.wp_type

    @property
    def skills(self):
        return self.template.skills

    def __repr__(self):
        return 'Wp<{0}>'.format(self.template.name)


class RankedWeapon:
    """ Weapon instance that a unit is holding """
    def __init__(self, weapon, rank):
        self.weapon = weapon
        self.rank = rank
        self.skills = [RankedSkill(s, rank) for s in self.weapon.skills]

    def __repr__(self):
        return 'RkWp<{0}:{1}>'.format(self.weapon.template.name, self.rank.name)


def load_all(root_path, get_skill):
    raw_weapons = data_loader.local_load(root_path + 'data/templates/weapons/', '.json')
    return [WeaponTemplate(name, data, get_skill) for name, data in raw_weapons.items()]
