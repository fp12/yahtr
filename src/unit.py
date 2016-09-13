from game import game_instance
from actions import ActionType, actions_trees
from rank import Rank
from skill import RankedSkill
from weapon import RankedWeapon


class Unit:
    def __init__(self, template_name):
        self.template_name = template_name
        raw_data = game_instance.classes[template_name]
        self.__dict__.update(raw_data)
        self.__dict__.update({'base_' + k: v for k, v in raw_data.items()})
        self.actions_tree = actions_trees[self.base_actions_tree_name]
        self.hex_coords = None
        self.orientation = None
        self.equipped_weapons = []
        self.owner = None

        if 'skills' in raw_data:
            self.base_skills = [RankedSkill(game_instance.get_skill(name), Rank[rank]) for name, rank in raw_data['skills'].items()]
            self.skills = self.base_skills[:]
        else:
            self.skills = self.base_skills = []

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
        if weapon.wp_type.name in self.weapons:
            rank = Rank[self.weapons[weapon.wp_type.name]]
            self.equipped_weapons.append(RankedWeapon(weapon, rank))

    def get_skills(self, action_type):
        skills = []
        if action_type == ActionType.Weapon:
            for ranked_weapon in self.equipped_weapons:
                skills.extend(ranked_weapon.weapon.skills)
        elif action_type == ActionType.Skill:
            skills = [rs.skill for rs in self.skills]
        return skills
