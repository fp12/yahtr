from collections import OrderedDict

from game import game_instance
from actions import ActionType, actions_trees


class Unit:
    def __init__(self, template_name):
        self.template_name = template_name
        self.__dict__.update(game_instance.classes[template_name])
        self.__dict__.update({'base_' + k: v for k, v in game_instance.classes[template_name].items()})
        self.actions_tree = actions_trees[self.base_actions_tree_name]
        self.hex_coords = None
        self.orientation = None
        self.equipped_weapons = []

        # 'fix' missing parameters
        if 'skills' not in self.__dict__:
            self.__dict__.update({'skills': {}, 'base_skills':{}})

    def __str__(self):
        return 'U<{0}>'.format(self.template_name)

    def __repr__(self):
        return 'U<{0}>'.format(self.template_name)

    def move_to(self, hex_coords=None, orientation=None):
        if hex_coords:
            self.hex_coords = hex_coords
        if orientation:
            self.orientation = orientation

    def equip(self, weapon):
        self.equipped_weapons.append(weapon)

    def get_skills(self, action_type):
        skills = OrderedDict()
        if action_type == ActionType.Weapon:
            for weapon in self.equipped_weapons:
                for skill_name in weapon.skills:
                    skill = game_instance.get_skill(skill_name)
                    if skill:
                        skills.update({skill_name: skill})
        elif action_type == ActionType.Skill:
            for skill_name in self.skills.keys():
                skill = game_instance.get_skill(skill_name)
                if skill:
                    skills.update({skill_name: skill})
        return skills