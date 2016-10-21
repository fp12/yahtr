from enum import Enum

from kivy.app import App
from kivy.properties import NumericProperty
from kivy.animation import Animation

from core.hex_lib import hex_angle, index_of_direction

from game import game_instance
from skill import MoveType
from utils import Color
import actions

from ui.hex_widget import HexWidget
from ui.tile import Tile
from ui.action_widgets import ActionBuilder
from ui.shield_widget import ShieldWidget
from ui.contour import Contour
from ui.base_widgets import AngledColoredWidget
from ui.utils import check_root_window


hit_color = Color.firebrick
contour_color = Color.forestgreen
contour_color.a = 0
reachable_color = Color.olivedrab
reachable_color.a = 0.5


class Status(Enum):
    Idle = 0
    Moving = 1


class PieceBody(HexWidget):
    pass


class PieceInterBody(AngledColoredWidget):
    pass


class Piece(HexWidget):
    angle = NumericProperty(0)

    def __init__(self, unit, **kwargs):
        super(Piece, self).__init__(q=unit.hex_coords.q, r=unit.hex_coords.r, **kwargs)
        self.unit = unit
        self.color = unit.color
        self.current_skill = None
        self.skill_widget = None
        self.status = Status.Idle
        self.selected = False
        self.reachable_tiles = []

        self._shape_parts = {}
        done_list = []
        for shape_part in self.unit.shape:
            part_hex = self.hex_coords + shape_part
            w = PieceBody(q=part_hex.q, r=part_hex.r, layout=self.hex_layout, color=self.color)
            self._shape_parts.update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1])})
            self.add_widget(w)

            for shape_part_other in self.unit.shape:
                same_shape_parts = shape_part == shape_part_other
                processed = (shape_part, shape_part_other) in done_list or (shape_part_other, shape_part) in done_list
                if not same_shape_parts and not processed and index_of_direction(shape_part_other - shape_part) != -1:
                    done_list.append((shape_part, shape_part_other))
                    hex_pos = self.hex_layout.hex_to_pixel(part_hex)
                    part_hex_other = self.hex_coords + shape_part_other
                    hex_pos_other = self.hex_layout.hex_to_pixel(part_hex_other)
                    size = (self.hex_layout.size.x, self.hex_layout.margin * 5)
                    pos = (hex_pos.x + (hex_pos_other.x - hex_pos.x) / 2 - size[0] / 2,
                           hex_pos.y + (hex_pos_other.y - hex_pos.y) / 2 - size[1] / 2)
                    angle = shape_part.angle_to_neighbour(shape_part_other - shape_part)
                    w = PieceInterBody(pos=pos, size=size, angle=angle, color=self.color, rotate_from_center=True)
                    self._shape_parts.update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1])})
                    self.add_widget(w)

        self.contour = Contour(unit.shape, layout=self.hex_layout, color=contour_color, pos=self.pos)
        self.add_widget(self.contour)

        self.do_rotate()
        self._shields = [{} for _ in range(len(unit.shields))]
        self.update_shields()

        # events
        self.unit.on_health_change += self.on_unit_health_change
        self.unit.on_shield_change += self.update_shields
        self.unit.on_skill_move += self.on_unit_skill_move

    def do_rotate(self):
        self.angle = self.hex_coords.angle_to_neighbour(self.unit.orientation)
        if self.skill_widget:
            self.skill_widget.angle = self.angle

    def update_shields(self):
        for shape_part_index, shape_part in enumerate(self.unit.shape):
            for shield_index in range(6):
                linear_index = shape_part_index * 6 + shield_index
                shield_value = self.unit.shields[linear_index]
                old_size = len(self._shields[linear_index])
                diff = shield_value - old_size
                if diff > 0:
                    for i in range(old_size, diff):
                        col = .6 - i * (0.6 / 3.)
                        shape_coord = self.hex_coords + shape_part
                        w = ShieldWidget(q=shape_coord.q, r=shape_coord.r,
                                         layout=self.hex_layout,
                                         color=[col, col, col, 1],
                                         radius=self.radius - (2 + 4) * i, thickness=8 - i * 2,
                                         angle=hex_angle(shield_index))
                        self.add_widget(w)
                        self._shields[linear_index].update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1], i)})
                elif diff < 0:
                    to_del = []
                    for shield_part, (_, _, order) in self._shields[linear_index].items():
                        print(shield_value, order, old_size)
                        if shield_value <= order < old_size:
                            self.remove_widget(shield_part)
                            to_del.append(shield_part)
                    for x in to_del:
                        del self._shields[linear_index][x]

    def on_finished_moving(self, trajectory, callback):
        self.status = Status.Idle
        previous = trajectory[-2] if len(trajectory) > 1 else self.hex_coords
        self.hex_coords = trajectory[-1]
        self.unit.move_to(hex_coords=self.hex_coords, orientation=trajectory[-1] - previous)
        if callback:
            callback(self)

    @check_root_window
    def on_pos(self, *args):
        self.contour.pos = self.pos
        for shape_part, offset in self._shape_parts.items():
            shape_part.pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])

        for shield_data in self._shields:
            for shield_part, (dx, dy, _) in shield_data.items():
                shield_part.pos = (self.pos[0] + dx, self.pos[1] + dy)

    @check_root_window
    def on_color_change(self, r, g, b, a):
        for shape_part, _ in self._shape_parts.items():
            shape_part.color = (r, g, b, a)

    def on_unit_health_change(self, health, context):
        pt = self.hex_layout.hex_to_pixel(self.hex_coords + context.direction)
        target_pos_x = self.x + (pt.x - self.x) / 10
        target_pos_y = self.y + (pt.y - self.y) / 10
        duration = 0.2
        anim = Animation(pos=(target_pos_x, target_pos_y), r=hit_color.r, g=hit_color.g, b=hit_color.b, duration=duration / 3)
        anim += Animation(pos=(self.x, self.y), r=self.r, g=self.g, b=self.b, duration=duration)

        app = App.get_running_app()
        app.anim_scheduler.add(anim, self, context.hit.order)

    def on_unit_skill_move(self, context):
        def on_skill_move_end(hex_coords, orientation):
            self.hex_coords = hex_coords
            self.unit.move_to(hex_coords, orientation)

        pos = self.hex_layout.hex_to_pixel(context.end_coords).tup if context.move_info.move else None

        anim = None
        if context.move_info.move_type == MoveType.none:
            anim = Animation(duration=0)
            if pos:
                anim &= Animation(pos=pos, duration=0.1)
            if context.move_info.orientation:
                if abs(context.target_angle - self.angle) > 180:
                    self.angle -= 360
                print(self.angle, context.target_angle)
                anim &= Animation(angle=context.target_angle, duration=0.2)
        elif context.move_info.move_type == MoveType.blink:
            anim = Animation(a=0, duration=0.1)
            if pos:
                anim += Animation(pos=pos, duration=0)
            if context.move_info.orientation:
                if abs(context.target_angle - self.angle) > 180:
                    self.angle -= 360
                print(self.angle, context.target_angle)
                anim += Animation(angle=context.target_angle, duration=0)
            anim += Animation(a=1, duration=0.2)
        elif context.move_info.move_type == MoveType.pushed:
            anim = Animation(pos=pos, duration=0.3, t='out_back')

        app = App.get_running_app()
        app.anim_scheduler.add(anim, self, context.move_info.order, lambda *args: on_skill_move_end(context.end_coords, context.end_orientation))

    def move_to(self, hex_coords, tile_pos=None, trajectory=[], on_move_end=None):
        """ override from HexWidget """
        if trajectory:
            self.clean_reachable_tiles()
            duration_per_tile = 0.2
            self.status = Status.Moving
            Animation.cancel_all(self)
            trajectory.remove(self.hex_coords)
            trajectory.reverse()
            anim = Animation(duration=0)
            prev_state = self.hex_coords, self.angle
            for h in trajectory:
                pos = self.hex_layout.hex_to_pixel(h)
                step_anim = Animation(pos=pos.tup, duration=duration_per_tile)
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

    def hex_test(self, hex_coords):
        return self.unit.hex_test(hex_coords)

    def load(self):
        self.update_shields()

    def clean_skill(self):
        if self.skill_widget:
            self.parent.remove_widget(self.skill_widget)
            self.skill_widget = None
        self.current_skill = None

    def load_skill(self, rk_skill):
        self.current_skill = rk_skill
        self.skill_widget = ActionBuilder(rk_skill, self.hex_coords, self.hex_layout, pos=self.pos, angle=self.angle)
        self.parent.add_widget(self.skill_widget)

    def display_reachable_tiles(self):
        if not self.reachable_tiles:
            reachable_hexes = game_instance.current_fight.current_map.get_reachable(self.unit)
            for hx in reachable_hexes:
                tile = Tile(hx.q, hx.r,
                            layout=self.hex_layout,
                            color=reachable_color,
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

    def on_action_change(self, action_type, rk_skill):
        self.clean_skill()
        if action_type == actions.ActionType.Move:
            self.display_reachable_tiles()
        else:
            self.clean_reachable_tiles()
            if rk_skill:
                self.load_skill(rk_skill)

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
                self.contour.a = 1
            else:
                self.clean_skill()
                self.clean_reachable_tiles()
                self.contour.a = 0
            self.selected = select
