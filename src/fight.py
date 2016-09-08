from game_map import Map
from time_bar import TimeBar


class Fight():
    def __init__(self, fight_map, players):
        self.current_map = Map(fight_map)
        self.squads = {p: [] for p in players}
        self.time_bar = TimeBar()
        self.started = False
        self.actions_history = []  # (unit, [ actions ])

    def deploy(self, squads):
        for squad_owner, units in squads.items():
            for player in self.squads.keys():
                if player == squad_owner:
                    self.squads[player] = units
                    self.current_map.register_units(units)
                    self.time_bar.register_units(units)

    def start(self):
        self.started = True

    def on_turn_end(self, unit, actions):
        self.actions_history.append((unit, actions))
