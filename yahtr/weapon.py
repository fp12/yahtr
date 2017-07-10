from yahtr.skill import RankedSkill


class Weapon:
    """ Weapon instance that a player is holding """

    def __init__(self, wp_template):
        self.template = wp_template

    @property
    def wp_type(self):
        return self.template.wp_type

    @property
    def skills(self):
        return self.template.skills

    def __repr__(self):
        return f'Wp<{self.template.name!s}>'


class RankedWeapon:
    """ Weapon instance that a unit is holding """

    def __init__(self, weapon, rank):
        self.weapon = weapon
        self.rank = rank
        self.skills = [RankedSkill(s, rank) for s in self.weapon.skills]

    def __repr__(self):
        return f'RkWp<{self.weapon.template.name!s}:{self.rank.name}>'
