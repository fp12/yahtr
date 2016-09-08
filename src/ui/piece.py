from math import cos, sin, pi
from enum import Enum
from functools import partial

from kivy.properties import NumericProperty
from kivy.animation import Animation

from ui.hex_widget import HexWidget
from ui.tile import Tile
from ui.action_arrow import ActionArrow
from ui.action_bubble import ActionBubble

from game import game_instance
from hex_lib import Hex
import pathfinding


class Status(Enum):
    Idle = 0
    Moving = 1


class Piece(HexWidget):
    angle = NumericProperty(0)

    def __init__(self, unit, **kwargs):
        self.unit = unit
        self.color = unit.color
        self._actions = []
        self._bubbles = []
        self._displayed_action = None
        self.status = Status.Idle
        self.selected = False
        self.reachable_tiles = []
        super(Piece, self).__init__(q=unit.hex_coords.q, r=unit.hex_coords.r, **kwargs)
        self.do_rotate()

    @property
    def actions_displayed(self):
        return len(self._bubbles) > 0

    def do_rotate(self):
        self.angle = self.hex_coords.angle_to_neighbour(self.unit.orientation)

    def on_finished_moving(self, trajectory, callback):
        self.status = Status.Idle
        self.selected = False
        previous = trajectory[-2] if len(trajectory) > 1 else self.hex_coords
        self.hex_coords = trajectory[-1]
        self.unit.move_to(hex_coords=self.hex_coords, orientation=trajectory[-1] - previous)
        if callback:
            callback(self)

    # override
    def move_to(self, hex_coords, tile_pos=None, trajectory=[], on_move_end=None):
        self.clear()
        if trajectory:
            duration_per_tile = 0.2
            self.status = Status.Moving
            Animation.cancel_all(self)
            trajectory.remove(self.hex_coords)
            trajectory.reverse()
            anim = Animation(duration=0)
            prev_state = self.hex_coords, self.angle
            for h in trajectory:
                pt = self.hex_layout.hex_to_pixel(h)
                step_anim = Animation(pos=(pt.x, pt.y), duration=duration_per_tile)
                prev_hex, prev_angle = prev_state
                angle = prev_hex.angle_to_neighbour(h-prev_hex)
                if angle != prev_angle:
                    if abs(prev_angle - angle) > 180:
                        angle += 360
                    step_anim &= Animation(angle=angle, duration=duration_per_tile / 3)
                anim += step_anim
                prev_state = h, angle
            anim.bind(on_complete=lambda *args: self.on_finished_moving(trajectory, on_move_end))
            anim.start(self)
        else:
            super(Piece, self).move_to(hex_coords, tile_pos, trajectory)

    def load(self):
        return
        for action in self.unit.actions.keys():
            if action in game_instance.actions:
                self._load_action(action)
                break

    def clear(self):
        self.clean_reachable_tiles()
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

    def display_reachable_tiles(self):
        assert(self.reachable_tiles == [])
        reachable_hexes = pathfinding.get_reachable(game_instance.current_fight.current_map, self.hex_coords, self.unit.move)
        for hx in reachable_hexes:
            tile = Tile(hx.q, hx.r, 
                        layout=self.hex_layout, 
                        color=[0.678431, 0.88, 0.184314, 0.2], 
                        radius=self.radius - 2, 
                        size=(self.radius - 2, self.radius - 2))
            self.parent.add_widget(tile)
            self.reachable_tiles.append(tile)

    def is_in_move_range(self, hex_coords):
        if self.reachable_tiles:
            for tile in self.reachable_tiles:
                if tile.hex_coords == hex_coords:
                    return True
        return False

    def clean_reachable_tiles(self):
        for tile in self.reachable_tiles:
            self.parent.remove_widget(tile)
        self.reachable_tiles = []

    def select_for_turn(self):
        self.display_reachable_tiles()
        self.selected = True

    def on_hovered_in(self):
        if not self.selected:
            self.display_reachable_tiles()

    def on_hovered_out(self):
        if not self.selected:
            self.clean_reachable_tiles()

    def on_touched_down(self):
        self.selected = True
        return True
        if not self._bubbles:
            action_count = len(self.unit.actions)
            angle = 60 if action_count < 6 else 30
            start_angle = -90 - (action_count - 1) * angle / 2
            distance = (self.hex_layout.size.x + self.hex_layout.size.y) / 2 * 1.5
            for i, action in zip(range(0, action_count), self.unit.actions):
                bubble = ActionBubble(i, action, self)
                self._bubbles.append(bubble)
                self.parent.add_widget(bubble)
                new_angle = (start_angle + i * angle) * pi / 180
                x = self.x + cos(new_angle) * distance
                y = self.y + sin(new_angle) * distance
                bubble.center = (x, y)
            return True
