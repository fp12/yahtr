from game_map import Map
from player import Player


class Fight():
    def __init__(self, fight_map, players):
        self.current_map = Map(fight_map)
        self.squads = {}
        for name, player_type in players.items():
            if player_type == 'player':
                self.squads.update({Player(name): None})
        self.started = False

    def deploy(self, squads):
        for player_name, units in squads.items():
            for player in self.squads.keys():
                if player.name == player_name:
                    self.squads[player] = units
                    continue

    def start(self):
        self.started = True
