from ui.hexagon import Hexagon
from ui.action_arrow import ActionArrow

from game import game_instance
from hex_lib import Hex


class Unit(Hexagon):
    def __init__(self, layout, template, q=0, r=0, **kwargs):
        super(Unit, self).__init__(layout, q, r, **kwargs)
        self._template = template
        self.color = template['color']
        self._actions = []
        self._displayed_action = None

    def load(self):
        for action in self._template['actions'].keys():
            if action in game_instance.actions:
                self._load_action(action)
                break

    def clear(self):
        for a in self._actions:
            self.parent.remove_widget(a)
        self._actions = []

    def _load_action(self, action):
        self._displayed_action = action
        for h in game_instance.actions[action]['hits']:
            origin = self._hex + Hex(qrs=h['origin'])
            direction = self._hex + Hex(qrs=h['direction'])
            pos = self._layout.get_mid_edge_position(origin, direction)
            angle = origin.angle_to_neighbour(direction)
            arrow = ActionArrow(angle=angle, pos=(pos.x, pos.y))
            self._actions.append(arrow)
            self.parent.add_widget(arrow)

    def on_cycle_action(self):
        for action in self._template['actions'].keys():
            if action != self._displayed_action and action in game_instance.actions:
                self.clear()
                self._load_action(action)
                break