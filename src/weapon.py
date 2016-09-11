from enum import Enum

from game import game_instance


class Type(Enum):
    Sword = 1
    Daggers = 2
    Spear = 3
    Scythe = 4


class Weapon:
    def __init__(self, template_name):
        self.template_name = template_name
        self.__dict__.update(game_instance.weapons_templates[template_name])
