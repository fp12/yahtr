from collections import OrderedDict

from yahtr.data.bank import data_bank
from yahtr.battle import Battle
from yahtr.tie import TieType
from yahtr.player import Player
from yahtr.player_ai import PlayerAI
from yahtr.unit import Unit
from yahtr.utils import Color
from yahtr.core.hex_lib import Hex


class Game():
    """ Class managing real time Game data """
    flat_layout = True

    def __init__(self, root_path=''):
        self.battle = None
        self.players = []

    def update(self, *args):
        if self.battle:
            self.battle.update(*args)

    def load_battle_setup(self, battle_setup_id):
        assert not self.battle
        setup = data_bank.get_battle_setup(battle_setup_id)
        assert setup is not None

        squads = OrderedDict()
        for player_info in setup.data['players']:
            player_class = Player if player_info['control'] == 'human' else PlayerAI
            p = player_class(self, player_info['name'], Color(player_info['color']))
            squads[p] = []
            for unit_info in player_info['squad']:
                template = data_bank.get_unit_template(unit_info['template'])
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

    def terminate(self):
        self.battle = None
        self.players = []


game_instance = Game()
