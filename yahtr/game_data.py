from yahtr.skill import load_all as load_all_skills
from yahtr.weapon import load_all as load_all_weapons
from yahtr.unit import load_all as load_all_units
from yahtr.actions import load_all as load_all_actions
from yahtr.battle_setup import load_all as load_all_battle_setups


class GameData:
    """ Class regrouping all static data loaded from files """

    def __init__(self):
        self.skills = []
        self.weapons_templates = []
        self.units_templates = []
        self.actions_trees = []
        self.boards = []
        self.battle_setups = []

    def load(self, root_path=''):
        self.skills = load_all_skills(root_path)
        self.actions_trees = load_all_actions(root_path)
        self.weapons_templates = load_all_weapons(root_path, self.get_skill)
        self.units_templates = load_all_units(root_path, self.get_skill, self.get_actions_tree)
        self.boards = []
        self.battle_setups = load_all_battle_setups(root_path)

    def get_skill(self, skill_id):
        for s in self.skills:
            if s.id == skill_id:
                return s
        return None

    def get_actions_tree(self, action_tree_id):
        for at in self.actions_trees:
            if at.id == action_tree_id:
                return at.tree
        return None

    def get_weapon_template(self, weapon_template_id):
        for w in self.weapons_templates:
            if w.id == weapon_template_id:
                return w
        return None

    def get_unit_template(self, unit_template_id):
        for u in self.units_templates:
            if u.id == unit_template_id:
                return u
        return None


game_data = GameData()
