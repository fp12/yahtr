from collections import OrderedDict

from game_data import game_data
from battle import Battle
from tie import TieType
from player import Player
from player_ai import PlayerAI
from unit import Unit
from utils import Color
from core.hex_lib import Hex
from utils.log import log_main


logger = log_main.getChild('game')


class Game():
    """ Class managing real time Game data """
    flat_layout = True

    def __init__(self, root_path=''):
        self.battle = None
        self.players = []

    def update(self, *args):
        if self.battle:
            self.battle.update(*args)

    def get_player(self, player_name):
        for p in self.players:
            if p.name == player_name:
                return p
        return None

    def load_battle_setup(self, battle_setup_id):
        assert not self.battle
        squads = OrderedDict()
        for setup in game_data.battle_setups:
            if setup.id == battle_setup_id:
                for player_info in setup.data['players']:
                    player_class = Player if player_info['control'] == 'human' else PlayerAI
                    p = player_class(self, player_info['name'], Color(player_info['color']))
                    squads[p] = []
                    for unit_info in player_info['squad']:
                        template = game_data.get_unit_template(unit_info['template'])
                        u = Unit(template)
                        for weapon_name in unit_info['weapons']:
                            w = p.add_weapon(weapon_name)
                            u.equip(w)
                        p.add_unit(u)
                        squads[p].append(u)
                        u.move_to(hex_coords=Hex(*unit_info['position']), orientation=Hex(*unit_info['orientation']))
                    self.players.append(p)

                self.battle = Battle(setup.data['board'], self.players)
                self.battle.set_tie(self.players[0], self.players[1], TieType.enemy)
                self.battle.deploy(squads)
                break


game_instance = Game()
