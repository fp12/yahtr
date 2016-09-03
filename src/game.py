import data_loader
import classes
from fight import Fight

class Game():
    def __init__(self, root_path=''):
        self._root_path = root_path
        self._actions = {}
        self._classes = classes.ClassesList()
        self._flat_layout = True
        self.current_fight = None

    def load(self):
        self._actions = data_loader.local_load(self._root_path + 'data/actions/', '.json')
        self._classes.local_load(self._root_path)

    def update_from_wiki(self):
        # print(self._classes.classes)
        added, changed, removed = self._classes.wiki_load()
        print(added, changed, removed)
        # print(self._classes.classes)

    def start_new_fight(self, fight_map, players):
        assert(self.current_fight == None)
        self.current_fight = Fight(fight_map, players)

    def deployment_finished(self, squads):
        self.current_fight.deploy(squads)
        self.current_fight.start()

    @property
    def actions(self):
        return self._actions

    @property
    def classes(self):
        return self._classes.classes

    @property
    def flat_layout(self):
        return self._flat_layout


if __name__ == '__main__':
    game_instance = Game('../')
    game_instance.load()
    game_instance.update_from_wiki()
else:
    game_instance = Game()
