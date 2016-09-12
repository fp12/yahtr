from enum import Enum

from game import game_instance


class Type(Enum):
    sword = 1
    daggers = 2
    spear = 3
    scythe = 4


class Weapon:
    def __init__(self, template_name):
        self.template_name = template_name
        raw_data = game_instance.weapons_templates[template_name]
        self.wp_type = Type[raw_data['type']]
        self.skills = []
        if 'skills' in raw_data:
            self.skills = [game_instance.get_skill(name) for name in raw_data['skills']]


class RankedWeaponType(Weapon):
    def __init__(self, wp_type, rank):
        self.wp_type = wp_type
        self.rank = rank
