import data_loader


class Game():
    def __init__(self):
        self._actions = {}
        self._units = {}
        self._flat_layout = True

    def load(self):
        self._actions = data_loader.simple_load('data/actions/', '.json')
        self._units = data_loader.simple_load('data/units/', '.json')

    @property
    def actions(self):
        return self._actions
    
    @property
    def units(self):
        return self._units

    @property
    def flat_layout(self):
        return self._flat_layout


game_instance = Game()
