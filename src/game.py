import data_loader
import classes
from fight import Fight
import skill


class Game():
    def __init__(self, root_path=''):
        self._root_path = root_path
        self.skills = []
        self._classes = classes.ClassesList()
        self.weapons_templates = {}
        self._flat_layout = True
        self.current_fight = None
        self.players = []

    def load(self):
        self.skills = skill.load_all(self._root_path)
        self.weapons_templates = data_loader.local_load(self._root_path + 'data/templates/weapons/', '.json')
        self._classes.local_load(self._root_path)

    def update_from_wiki(self):
        # print(self._classes.classes)
        added, changed, removed = self._classes.wiki_load()
        print(added, changed, removed)
        # print(self._classes.classes)

    def register_player(self, player):
        self.players.append(player)

    def get_player(self, player_name):
        for p in self.players:
            if p.name == player_name:
                return p

    def get_skill(self, skill_name):
        for s in self.skills:
            if s.name == skill_name:
                return s
        return None

    def prepare_new_fight(self, fight_map, players):
        assert(not self.current_fight)
        self.current_fight = Fight(fight_map, players)

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
