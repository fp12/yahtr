from game import game_instance
from actions import actions_trees


class Unit:
    def __init__(self, template_name):
        self.template_name = template_name
        self.__dict__.update(game_instance.classes[template_name])
        self.__dict__.update({'base_' + k: v for k, v in game_instance.classes[template_name].items()})
        self.actions_tree = actions_trees[self.base_actions_tree_name]
        self.hex_coords = None
        self.orientation = None

    def __str__(self):
        return 'U<{0}>'.format(self.template_name)

    def __repr__(self):
        return 'U<{0}>'.format(self.template_name)

    def move_to(self, hex_coords=None, orientation=None):
        if hex_coords:
            self.hex_coords = hex_coords
        if orientation:
            self.orientation = orientation
