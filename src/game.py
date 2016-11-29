from collections import OrderedDict

from battle import Battle
import skill
import weapon
import unit
import actions
import battle_setups
import tie
from player import Player
from player_ai import PlayerAI
from unit import Unit
from utils import Color
from core.hex_lib import Hex
from utils.log import log_main


logger = log_main.getChild('game')


class Game():
    def __init__(self, root_path=''):
        self._root_path = root_path
        self.skills = []
        self.weapons_templates = []
        self.units_templates = []
        self.actions_trees = []
        self.battle_setups = []
        self.battle = None
        self.players = []

    def load(self):
        self.skills = skill.load_all(self._root_path)
        self.actions_trees = actions.load_all(self._root_path)
        self.weapons_templates = weapon.load_all(self._root_path, self.get_skill)
        self.units_templates = unit.load_all(self._root_path, self.get_skill, self.get_actions_tree)
        self.battle_setups = battle_setups.load_all(self._root_path)

    def update_from_wiki(self):
        added, changed, removed = self._classes.wiki_load()

    def update(self, *args):
        if self.battle:
            self.battle.update(*args)

    def get_player(self, player_name):
        for p in self.players:
            if p.name == player_name:
                return p
        return None

    def get_skill(self, name):
        for s in self.skills:
            if s.name == name:
                return s
        logger.warning('can\'t find Skill [{}]'.format(name))
        return None

    def get_actions_tree(self, name):
        for at in self.actions_trees:
            if at.name == name:
                return at.tree
        logger.warning('can\'t find Action Tree [{}]'.format(name))
        return None

    def get_weapon_template(self, name):
        for w in self.weapons_templates:
            if w.name == name:
                return w
        logger.warning('can\'t find Weapon Template [{}]'.format(name))
        return None

    def get_unit_template(self, name):
        for u in self.units_templates:
            if u.name == name:
                return u
        logger.warning('can\'t find Unit Template [{}]'.format(name))
        return None

    def load_battle_setup(self, name):
        assert not self.battle
        squads = OrderedDict()
        for setup in self.battle_setups:
            if setup.name == name:
                for player_info in setup.data['players']:
                    player_class = Player if player_info['control'] == 'human' else PlayerAI
                    p = player_class(self, player_info['name'], Color(player_info['color']))
                    squads[p] = []
                    for unit_info in player_info['squad']:
                        template = self.get_unit_template(unit_info['template'])
                        u = Unit(template)
                        for weapon_name in unit_info['weapons']:
                            w = p.add_weapon(weapon_name)
                            u.equip(w)
                        p.add_unit(u)
                        squads[p].append(u)
                        u.move_to(hex_coords=Hex(*unit_info['position']), orientation=Hex(*unit_info['orientation']))
                    self.players.append(p)

                self.battle = Battle(setup.data['board'], self.players)
                self.battle.set_tie(self.players[0], self.players[1], tie.Type.Enemy)
                self.battle.deploy(squads)
                break

    @property
    def flat_layout(self):
        return True


if __name__ == '__main__':
    game_instance = Game('../')
    game_instance.load()
    game_instance.update_from_wiki()
else:
    game_instance = Game()
