class Player():
    def __init__(self, name):
        self.name = name
        self.units = []

    def add_unit(self, unit):
        unit.owner = self
        self.units.append(unit)

    def __str__(self):
        return 'P<{0}>'.format(self.name)
