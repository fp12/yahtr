from game import game_instance


class Unit(object):
    def __init__(self, template_name):
        self.template_name = template_name
        self.__dict__.update(game_instance.classes[template_name])
        self.hex_coords = None

    def __str__(self):
        return 'U<{0}>'.format(self.template_name)

    def __repr__(self):
        return 'U<{0}>'.format(self.template_name)
