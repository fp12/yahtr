from yahtr.weapon import Weapon
from yahtr.game_data import game_data


class Player():
    ai_controlled = False

    def __init__(self, game, name, color):
        self.game = game
        self.name = name
        self.color = color
        self.units = []
        self.weapons = []

    def add_unit(self, unit):
        unit.owner = self
        self.units.append(unit)

    def add_weapon(self, weapon_template):
        w = Weapon(game_data.get_weapon_template(weapon_template))
        self.weapons.append(w)
        return w

    def __repr__(self):
        return f'P<{self.name}>'
