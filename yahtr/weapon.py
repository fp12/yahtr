from enum import Enum

from yahtr.data_loader import local_load
from yahtr.skill import RankedSkill
from yahtr.utils import attr


class Type(Enum):
    sword = 1
    daggers = 2
    spear = 3
    scythe = 4
    grimoire = 5


class WeaponTemplate:
    """ Weapon as defined in data """

    __attributes = ['name', 'description']

    def __init__(self, file, data, get_skill):
        self.id = file
        attr.get_from_dict(self, data, *WeaponTemplate.__attributes)
        self.wp_type = Type[data['type']]
        self.skills = [get_skill(s) for s in data['skills']] if 'skills' in data else []

    def __repr__(self):
        return f'WpTp<{self.name}>'


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
        return f'Wp<{self.template.name}>'


class RankedWeapon:
    """ Weapon instance that a unit is holding """

    def __init__(self, weapon, rank):
        self.weapon = weapon
        self.rank = rank
        self.skills = [RankedSkill(s, rank) for s in self.weapon.skills]

    def __repr__(self):
        return f'RkWp<{self.weapon.template.name}:{self.rank.name}>'


def load_all(root_path, get_skill):
    raw_weapons = local_load(root_path + 'data/templates/weapons/', '.json')
    return [WeaponTemplate(file, data, get_skill) for file, data in raw_weapons.items()]
