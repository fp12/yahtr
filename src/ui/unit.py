from math import cos, sin, pi
from enum import Enum
from functools import partial

from kivy.animation import Animation

from ui.hex_widget import HexWidget
from ui.action_arrow import ActionArrow
from ui.action_bubble import ActionBubble

from game import game_instance
from hex_lib import Hex


class Status(Enum):
    Idle = 0
    Moving = 1


class Unit(HexWidget):
    def __init__(self, template, **kwargs):
        super(Unit, self).__init__(**kwargs)
        self._template = template
        self.color = template['color']
        self._actions = []
        self._bubbles = []
        self._displayed_action = None
        self.status = Status.Idle
        self.selected = False

    @property
    def actions_displayed(self):
        return len(self._bubbles) > 0

    def on_finished_moving(self, hex_coords, callback):
        self.status = Status.Idle
        self.selected = False
        self.hex_coords = hex_coords
        if callback:
            callback()

    # override
    def move_to(self, hex_coords, tile_pos=None, trajectory=[], on_move_end=None):
        self.clear()
        if trajectory:
            self.status = Status.Moving
            Animation.cancel_all(self)
            trajectory.remove(self.hex_coords)
            trajectory.reverse()
            anim = Animation(duration=0)
            for hex_coords in trajectory:
                pt = self.hex_layout.hex_to_pixel(hex_coords)
                anim += Animation(pos=(pt.x, pt.y), duration=0.2)
            anim.bind(on_complete=lambda *args: self.on_finished_moving(hex_coords, on_move_end))
            anim.start(self)
        else:
            super(Unit, self).move_to(hex_coords, tile_pos, trajectory)

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
            origin = self.hex_coords + Hex(qrs=h['origin'])
            direction = self.hex_coords + Hex(qrs=h['direction'])
            pos = self.hex_layout.get_mid_edge_position(origin, direction)
            angle = origin.angle_to_neighbour(direction)
            arrow = ActionArrow(angle=angle, pos=(pos.x, pos.y))
            self._actions.append(arrow)
            self.parent.add_widget(arrow)

    def on_real_touch_down(self):
        self.selected = True
        return True
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
