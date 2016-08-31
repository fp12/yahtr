from math import cos, sin, pi

from ui.hexagon import Hexagon
from ui.action_arrow import ActionArrow
from ui.action_bubble import ActionBubble

from game import game_instance
from hex_lib import Hex, Point


class Unit(Hexagon):
    def __init__(self, layout, template, q=0, r=0, **kwargs):
        super(Unit, self).__init__(layout, q, r, **kwargs)
        self._template = template
        self.color = template['color']
        self._actions = []
        self._bubbles = []
        self._displayed_action = None

    @property
    def actions_displayed(self):
        return len(self._bubbles) > 0 
    
    def move_to(self, hex_coords, tile_pos=None):
        self.clear()
        super(Unit, self).move_to(hex_coords, tile_pos)


    def load(self):
        return
        for action in self._template['actions'].keys():
            if action in game_instance.actions:
                self._load_action(action)
                break

    def clear(self):
        for a in self._actions:
            self.parent.remove_widget(a)
        self._actions = []
        for b in self._bubbles:
            b.clear()
            self.parent.remove_widget(b)
        self._bubbles = []

    def load_action(self, action):
        self._displayed_action = action
        for h in game_instance.actions[action]['hits']:
            origin = self._hex + Hex(qrs=h['origin'])
            direction = self._hex + Hex(qrs=h['direction'])
            pos = self.hex_layout.get_mid_edge_position(origin, direction)
            angle = origin.angle_to_neighbour(direction)
            arrow = ActionArrow(angle=angle, pos=(pos.x, pos.y))
            self._actions.append(arrow)
            self.parent.add_widget(arrow)

    def on_real_touch_down(self):
        if not self._bubbles:
            action_count = len(self._template['actions'])
            angle = 60 if action_count < 6 else 30
            start_angle = -90 - (action_count - 1) * angle / 2
            distance = (self.hex_layout.size.x + self.hex_layout.size.y) / 2 * 1.5
            for i, action in zip(range(0, action_count), self._template['actions']):
                bubble = ActionBubble(i, action, self)
                self._bubbles.append(bubble)
                self.parent.add_widget(bubble)
                new_angle = (start_angle + i * angle) * pi / 180
                x = self.x + cos(new_angle) * distance
                y = self.y + sin(new_angle) * distance
                bubble.center = (x, y)
            return True
