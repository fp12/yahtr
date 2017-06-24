class RankedSkill:
    """ Skill instanciated inside a weapon or a unit """

    def __init__(self, skill, rank):
        self.skill = skill
        self.rank = rank

    def __repr__(self):
        return f'RkSk<{self.skill.name}:{self.rank.name}>'

    def hit_value(self, hit):
        return hit.values[self.rank.value]
