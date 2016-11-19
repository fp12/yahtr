from battle import Battle
import skill
import weapon
import unit


class Game():
    def __init__(self, root_path=''):
        self._root_path = root_path
        self.skills = []
        self.weapons_templates = []
        self.units_templates = []
        self._flat_layout = True
        self.battle = None
        self.players = []

    def load(self):
        self.skills = skill.load_all(self._root_path)
        self.weapons_templates = weapon.load_all(self._root_path, self.get_skill)
        self.units_templates = unit.load_all(self._root_path, self.get_skill)

    def update_from_wiki(self):
        # print(self._classes.classes)
        added, changed, removed = self._classes.wiki_load()
        print(added, changed, removed)
        # print(self._classes.classes)

    def update(self, *args):
        if self.battle:
            self.battle.update(*args)

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

    def get_weapon_template(self, weapon_template_name):
        for w in self.weapons_templates:
            if w.name == weapon_template_name:
                return w
        return None

    def get_unit_template(self, unit_template_name):
        for u in self.units_templates:
            if u.name == unit_template_name:
                return u
        return None

    def prepare_new_battle(self, battle_board, players):
        assert not self.battle
        self.battle = Battle(battle_board, players)

    @property
    def flat_layout(self):
        return self._flat_layout


if __name__ == '__main__':
    game_instance = Game('../')
    game_instance.load()
    game_instance.update_from_wiki()
else:
    game_instance = Game()
