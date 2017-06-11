from yahtr.skill import load_all_skills, load_one_skill
from yahtr.weapon import load_all_weapon_templates, load_one_weapon_template
from yahtr.unit import load_all_unit_templates, load_one_unit_template
from yahtr.actions import load_all_actions_trees, load_one_actions_tree
from yahtr.board import load_all_board_templates, load_one_board_template
from yahtr.battle_setup import load_all_battle_setups, load_one_battle_setup


class GameData:
    """ Class regrouping all static data loaded from files """

    def __init__(self):
        self.skills = []
        self.actions_trees = []
        self.weapon_templates = []
        self.unit_templates = []
        self.board_templates = []
        self.battle_setups = []

    def load_all(self):
        self.skills = load_all_skills()
        self.actions_trees = load_all_actions_trees()
        self.weapon_templates = load_all_weapon_templates(self.get_skill)
        self.unit_templates = load_all_unit_templates(self.get_skill, self.get_actions_tree)
        self.board_templates = load_all_board_templates()
        self.battle_setups = load_all_battle_setups()

    def get_skill(self, skill_id):
        for s in self.skills:
            if s.id == skill_id:
                return s
        data = load_one_skill(skill_id)
        if data:
            self.skills.append(data)
        return data

    def get_actions_tree(self, actions_tree_id):
        for at in self.actions_trees:
            if at.id == actions_tree_id:
                return at.tree
        data = load_one_actions_tree(actions_tree_id)
        if data:
            self.actions_trees.append(data)
        return data.tree

    def get_weapon_template(self, weapon_template_id):
        for w in self.weapon_templates:
            if w.id == weapon_template_id:
                return w
        data = load_one_weapon_template(weapon_template_id, self. get_skill)
        if data:
            self.weapon_templates.append(data)
        return data

    def get_unit_template(self, unit_template_id):
        for u in self.unit_templates:
            if u.id == unit_template_id:
                return u
        data = load_one_unit_template(unit_template_id, self.get_skill, self.get_actions_tree)
        if data:
            self.unit_templates.append(data)
        return data

    def get_board_template(self, board_id):
        for b in self.board_templates:
            if b.id == board_id:
                return b
        data = load_one_board_template(board_id)
        if data:
            self.board_templates.append(data)
        return data

    def get_battle_setup(self, battle_setup_id):
        for b in self.battle_setups:
            if b.id == battle_setup_id:
                return b
        data = load_one_battle_setup(battle_setup_id)
        if data:
            self.battle_setups.append(data)
        return data


game_data = GameData()
