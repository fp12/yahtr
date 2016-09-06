from game import game_instance


class Unit:
    def __init__(self, template_name):
        self.template_name = template_name
        self.template = game_instance.classes[template_name]
        self.game_stats = {'hex_coord': None}

    def __str__(self):
        return 'U<{0}>'.format(self.template_name)
