from math import cos, sin, pi
from enum import Enum

from kivy.properties import NumericProperty
from kivy.animation import Animation

from ui.hex_widget import HexWidget
from ui.tile import Tile
from ui.action_arrow import ActionArrow
from ui.shield_widget import ShieldWidget
from ui.selector import Selector

from game import game_instance
from hex_lib import Hex
import pathfinding
import actions


class Status(Enum):
    Idle = 0
    Moving = 1


class Piece(HexWidget):
    angle = NumericProperty(0)

    def __init__(self, unit, **kwargs):
        self.unit = unit
        self.color = unit.color
        self._actions = []
        self._shields = [[] for _ in range(6)]
        self._displayed_action = None
        self.status = Status.Idle
        self.selected = False
        self.reachable_tiles = []
        super(Piece, self).__init__(q=unit.hex_coords.q, r=unit.hex_coords.r, **kwargs)

        self._selection_widget = Selector(q=unit.hex_coords.q, r=unit.hex_coords.r, layout=self.hex_layout, margin=2.5, color=[0.1, 0.9, 0.2, 0])
        self.add_widget(self._selection_widget)
        self.do_rotate()
        self.update_shields()

    def do_rotate(self):
        self.angle = self.hex_coords.angle_to_neighbour(self.unit.orientation)

    def update_shields(self):
        for index, shield_value in enumerate(self.unit.shields):
            old_size = len(self._shields[index])
            diff = shield_value - old_size
            if diff > 0:
                for i in range(old_size, diff):
                    col = .6 - i * (0.6 / 3.)
                    w = ShieldWidget(q=self.hex_coords.q, r=self.hex_coords.r,
                                     layout=self.hex_layout,
                                     color=[col, col, col, 1],
                                     radius=self.radius - (2 + 4) * i, thickness=8 - i * 2,
                                     angle=Hex.angles[index])
                    self.add_widget(w)
                    self._shields[index].append(w)

    def on_finished_moving(self, trajectory, callback):
        self.status = Status.Idle
        previous = trajectory[-2] if len(trajectory) > 1 else self.hex_coords
        self.hex_coords = trajectory[-1]
        self.unit.move_to(hex_coords=self.hex_coords, orientation=trajectory[-1] - previous)
        if callback:
            callback(self)

    def on_pos(self, *args):
        for c in self.children:
            c.pos = self.pos

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
                angle = prev_hex.angle_to_neighbour(h - prev_hex)
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
        self.update_shields()

    def clear(self):
        self.clean_reachable_tiles()
        for a in self._actions:
            self.parent.remove_widget(a)
        self._actions = []

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
        if not self.reachable_tiles:
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

    def on_action_change(self, action_type):
        if action_type == actions.ActionType.Move:
            self.display_reachable_tiles()
        else:
            self.clean_reachable_tiles()

    def on_hovered_in(self):
        if not self.selected:
            self.display_reachable_tiles()

    def on_hovered_out(self):
        if not self.selected:
            self.clean_reachable_tiles()

    def on_touched_down(self):
        self.do_select(True)
        return True

    def do_select(self, select):
        if self.selected != select:
            if select:
                self.display_reachable_tiles()
                self._selection_widget.a = 1
            else:
                self.clean_reachable_tiles()
                self._selection_widget.a = 0
            self.selected = select
