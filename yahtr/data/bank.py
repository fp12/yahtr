from yahtr.data.skill_template import SkillTemplate
from yahtr.data.weapon_template import WeaponTemplate
from yahtr.data.unit_template import UnitTemplate
from yahtr.data.actions import ActionsTree
from yahtr.data.board_template import BoardTemplate
from yahtr.data.battle_setup import BattleSetup


class Bank:
    """ Class regrouping all static data loaded from files """

    def __init__(self):
        self.skills = []
        self.actions_trees = []
        self.weapon_templates = []
        self.unit_templates = []
        self.board_templates = []
        self.battle_setups = []

    def load_all(self):
        self.skills = SkillTemplate.load_all()
        self.actions_trees = ActionsTree.load_all()
        self.weapon_templates = WeaponTemplate.load_all(self.get_skill)
        self.unit_templates = UnitTemplate.load_all(self.get_skill, self.get_actions_tree)
        self.board_templates = BoardTemplate.load_all()
        self.battle_setups = BattleSetup.load_all()

    def unload_all(self):
        self.skills = []
        self.actions_trees = []
        self.weapon_templates = []
        self.unit_templates = []
        self.board_templates = []
        self.battle_setups = []

    def get_skill(self, skill_id):
        for s in self.skills:
            if s.id == skill_id:
                return s
        data = SkillTemplate.load_one(skill_id)
        if data:
            self.skills.append(data)
        return data

    def get_actions_tree(self, actions_tree_id):
        for at in self.actions_trees:
            if at.id == actions_tree_id:
                return at.tree
        data = ActionsTree.load_one(actions_tree_id)
        if data:
            self.actions_trees.append(data)
        return data.tree

    def get_weapon_template(self, weapon_template_id):
        for w in self.weapon_templates:
            if w.id == weapon_template_id:
                return w
        data = WeaponTemplate.load_one(weapon_template_id, self. get_skill)
        if data:
            self.weapon_templates.append(data)
        return data

    def get_unit_template(self, unit_template_id):
        for u in self.unit_templates:
            if u.id == unit_template_id:
                return u
        data = UnitTemplate.load_one(unit_template_id, self.get_skill, self.get_actions_tree)
        if data:
            self.unit_templates.append(data)
        return data

    def get_board_template(self, board_id):
        for b in self.board_templates:
            if b.id == board_id:
                return b
        data = BoardTemplate.load_one(board_id)
        if data:
            self.board_templates.append(data)
        return data

    def get_battle_setup(self, battle_setup_id):
        for b in self.battle_setups:
            if b.id == battle_setup_id:
                return b
        data = BattleSetup.load_one(battle_setup_id)
        if data:
            self.battle_setups.append(data)
        return data


data_bank = Bank()
