from game_map import Map


class Fight():
    def __init__(self, fight_map, players=[]):
        self.current_map = Map(fight_map)
        self.squads = {p: None for p in players}

    def deploy(self, squads):
        for player, units in squads.items():
            if player in self.squads:
                self.squads[player] = units

    def start(self):
        # start the Time battle
        pass
