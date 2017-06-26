from yahtr.data.skill_template import SkillTemplate
from yahtr.data.weapon_template import WeaponTemplate
from yahtr.data.unit_template import UnitTemplate
from yahtr.data.actions import ActionsTree
from yahtr.data.board_template import BoardTemplate
from yahtr.data.battle_setup import BattleSetup
from yahtr.utils.log import create_system_logger


logger = create_system_logger('DataBank')


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
        self.skills = SkillTemplate.load_all(parent=self)
        self.actions_trees = ActionsTree.load_all(parent=self)
        self.weapon_templates = WeaponTemplate.load_all(self.get_skill, parent=self)
        self.unit_templates = UnitTemplate.load_all(self.get_skill, self.get_actions_tree, parent=self)
        self.board_templates = BoardTemplate.load_all(parent=self)
        self.battle_setups = BattleSetup.load_all(parent=self)

    def unload_all(self):
        self.skills = []
        self.actions_trees = []
        self.weapon_templates = []
        self.unit_templates = []
        self.board_templates = []
        self.battle_setups = []

    def get_dependency_tree(self):
        for s in self.skills:
            logger.info('{0} requested by : {1}'.format(s.file_id, s.parents))

    def get_skill(self, skill_id, parent=None):
        for s in self.skills:
            if s.file_id == skill_id:
                if parent:
                    s.add_dependency(parent)
                return s
        data = SkillTemplate.load_one(skill_id, parent=parent)
        if data:
            self.skills.append(data)
        return data

    def get_actions_tree(self, actions_tree_id, parent=None):
        for at in self.actions_trees:
            if at.file_id == actions_tree_id:
                if parent:
                    at.add_dependency(parent)
                return at.tree
        data = ActionsTree.load_one(actions_tree_id, parent=parent)
        if data:
            self.actions_trees.append(data)
        return data.tree

    def get_weapon_template(self, weapon_template_id, parent=None):
        for w in self.weapon_templates:
            if w.file_id == weapon_template_id:
                if parent:
                    w.add_dependency(parent)
                return w
        data = WeaponTemplate.load_one(weapon_template_id, self.get_skill, parent=self)
        if data:
            self.weapon_templates.append(data)
        return data

    def get_unit_template(self, unit_template_id, parent=None):
        for u in self.unit_templates:
            if u.file_id == unit_template_id:
                if parent:
                    u.add_dependency(parent)
                return u
        data = UnitTemplate.load_one(unit_template_id, self.get_skill, self.get_actions_tree, parent=parent)
        if data:
            self.unit_templates.append(data)
        return data

    def get_board_template(self, board_id, parent=None):
        for b in self.board_templates:
            if b.file_id == board_id:
                if parent:
                    b.add_dependency(parent)
                return b
        data = BoardTemplate.load_one(board_id, parent=parent)
        if data:
            self.board_templates.append(data)
        return data

    def get_battle_setup(self, battle_setup_id, parent=None):
        for b in self.battle_setups:
            if b.file_id == battle_setup_id:
                if parent:
                    b.add_dependency(parent)
                return b
        data = BattleSetup.load_one(battle_setup_id, parent=parent)
        if data:
            self.battle_setups.append(data)
        return data


data_bank = Bank()
