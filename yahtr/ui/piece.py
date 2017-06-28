from enum import Enum

from kivy.properties import NumericProperty, ListProperty
from kivy.animation import Animation

from yahtr.core.hex_lib import hex_angle, index_of_direction

from yahtr.game import game_instance
from yahtr.data.skill_template import MoveType
from yahtr.utils import Color
from yahtr.utils.event import Event
from yahtr.data.actions import ActionType

from yahtr.ui.anim_scheduler import anim_scheduler
from yahtr.ui.hex_widget import HexWidget
from yahtr.ui.tile import Tile
from yahtr.ui.action_widgets import ActionBuilder
from yahtr.ui.shield_widget import ShieldWidget
from yahtr.ui.contour import Contour
from yahtr.ui.base_widgets import AngledColoredWidget
from yahtr.ui.utils import check_root_window


c_hit = Color.firebrick
c_heal = Color.lightgreen
c_contour = Color.forestgreen
c_contour.a = 0
c_reachable_selected = Color(113, 20, 204, 128)
c_reachable_not_selected = Color(94, 9, 78, 128)


class Status(Enum):
    idle = 0
    moving = 1


class PieceBody(HexWidget):
    pass


class PieceInterBody(AngledColoredWidget):
    pass


class Piece(HexWidget):
    angle = NumericProperty(0)
    squad_color = ListProperty([])

    def __init__(self, unit, **kwargs):
        super(Piece, self).__init__(q=unit.hex_coords.q, r=unit.hex_coords.r, **kwargs)
        self.unit = unit
        self.color = unit.color
        self.squad_color = unit.owner.color.rgb + [self.a]
        self.current_skill = None
        self.skill_widget = None
        self.status = Status.idle
        self.selected = False
        self.reachable_tiles = []

        self.shape_parts = {}
        done_list = []
        for shape_part in self.unit.shape:
            part_hex = self.hex_coords + shape_part
            w = PieceBody(q=part_hex.q, r=part_hex.r, layout=self.hex_layout, color=self.color)
            self.shape_parts.update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1])})
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
                    self.shape_parts.update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1])})
                    self.add_widget(w)

        self.contour = Contour(unit.shape, layout=self.hex_layout, color=c_contour, pos=self.pos)
        self.add_widget(self.contour)

        self.do_rotate()
        self.shields = [{} for __ in unit.shields]
        self.update_shields()

        # declare events
        self.on_status_change = Event('new_status')

        # register to events
        self.unit.on_health_change += self.on_unit_health_change
        self.unit.on_unit_targeted += self.on_unit_targeted
        self.unit.on_shield_change += self.update_shields
        self.unit.on_shield_targeted += self.on_shield_targeted
        self.unit.on_targeted_end += self.on_targeted_end
        self.unit.on_sim_move += self.on_unit_sim_move
        self.unit.on_skill_move += self.on_unit_skill_move

    def load(self):
        self.update_shields()

    def unload(self):
        self.clean_reachable_tiles()

    def do_rotate(self):
        self.angle = self.hex_coords.angle_to_neighbour(self.unit.orientation)
        if self.skill_widget:
            self.skill_widget.angle = self.angle

    def change_status(self, new_status):
        if new_status != self.status:
            self.status = new_status
            self.on_status_change(self.status)

#    ######  ##     ## #### ######## ##       ########   ######
#   ##    ## ##     ##  ##  ##       ##       ##     ## ##    ##
#   ##       ##     ##  ##  ##       ##       ##     ## ##
#    ######  #########  ##  ######   ##       ##     ##  ######
#         ## ##     ##  ##  ##       ##       ##     ##       ##
#   ##    ## ##     ##  ##  ##       ##       ##     ## ##    ##
#    ######  ##     ## #### ######## ######## ########   ######
#   ############################################################

    def get_shield_thickness(self):
        return self.radius / 7

    def get_shield_radius(self, order):
        return self.radius - self.get_shield_thickness() * order

    @staticmethod
    def get_shield_color(index):
        col = .6 - index * (0.6 / 3.)
        return [col, col, col, 1]

    def update_shields(self):
        def del_part(anim, widget):
            self.remove_widget(widget)
            for d in self.shields:
                if widget in d:
                    del d[widget]
                    return

        for shape_part_index, shape_part in enumerate(self.unit.shape):
            for shield_index in range(6):
                linear_index = shape_part_index * 6 + shield_index
                shield_value = self.unit.shields[linear_index]
                old_size = len(self.shields[linear_index])
                diff = shield_value - old_size
                if diff > 0:
                    for i in range(old_size, diff):
                        shape_coord = self.hex_coords + shape_part
                        w = ShieldWidget(q=shape_coord.q, r=shape_coord.r,
                                         layout=self.hex_layout,
                                         color=self.get_shield_color(i),
                                         thickness=self.get_shield_thickness(),
                                         radius=self.get_shield_radius(i),
                                         angle=hex_angle(shield_index))
                        self.add_widget(w)
                        self.shields[linear_index].update({w: (w.pos[0] - self.pos[0], w.pos[1] - self.pos[1], i)})
                elif diff < 0:
                    for shield_part, (__, __, order) in self.shields[linear_index].items():
                        if shield_value <= order < old_size:
                            shield_part.color = c_hit
                            anim = Animation(thickness=shield_part.thickness * 2, a=0, duration=0.5, t='in_out_circ')
                            anim_scheduler.add(anim, shield_part, 0, del_part)

    def on_shield_targeted(self, shield_index):
        shield_part = max(self.shields[shield_index], key=lambda k: self.shields[shield_index][k][2])
        duration = 3
        anim = Animation(**c_hit.rgb_dict, duration=duration / 3)
        anim += Animation(r=shield_part.r, g=shield_part.g, b=shield_part.b, duration=duration * 2 / 3)
        anim.repeat = True
        anim.start(shield_part)

    def _on_targeted_end_shields(self, shield_index):
        shield_part = max(self.shields[shield_index], key=lambda k: self.shields[shield_index][k][2])
        Animation.cancel_all(shield_part)
        shield_part.color = self.get_shield_color(self.shields[shield_index][shield_part][2])

#   ##     ##  #######  ##     ## ########
#   ###   ### ##     ## ##     ## ##
#   #### #### ##     ## ##     ## ##
#   ## ### ## ##     ## ##     ## ######
#   ##     ## ##     ##  ##   ##  ##
#   ##     ## ##     ##   ## ##   ##
#   ##     ##  #######     ###    ########
#   ######################################

    def on_unit_sim_move(self, trajectory, orientation):
        if trajectory:
            self.move_to(hex_coords=trajectory[-1], trajectory=trajectory)

        if orientation:
            self.unit.move_to(orientation=orientation)
            self.do_rotate()

    def prepare_move(self):
        self.contour.hide()
        self.clean_skill()
        self.clean_reachable_tiles()
        self.change_status(Status.moving)

    def on_unit_skill_move(self, context):
        self.prepare_move()

        pos = self.hex_layout.hex_to_pixel(context.end_coords).tup if context.move_info.move else None

        anim = None
        if context.move_info.move_type == MoveType.none:
            anim = Animation(duration=0)
            if pos:
                anim &= Animation(pos=pos, duration=0.3)
            if context.move_info.orientation:
                if abs(context.target_angle - self.angle) > 180:
                    self.angle -= 360
                anim &= Animation(angle=context.target_angle, duration=0.2)

        elif context.move_info.move_type == MoveType.blink:
            anim = Animation(a=0, duration=0.1)
            if pos:
                anim += Animation(pos=pos, duration=0)
            if context.move_info.orientation:
                if abs(context.target_angle - self.angle) > 180:
                    self.angle -= 360
                anim += Animation(angle=context.target_angle, duration=0)
            anim += Animation(a=1, duration=0.2)

        elif context.move_info.move_type == MoveType.pushed:
            anim = Animation(pos=pos, duration=0.3, t='out_back')

        elif context.move_info.move_type == MoveType.jump_over_tile:
            duration = 1
            target_pos_x = self.x - (pos[0] - self.x) / 30
            target_pos_y = self.y - (pos[1] - self.y) / 30

            prep_anim = Animation(radius=self.radius * .95, duration=duration / 3)
            prep_anim &= Animation(pos=(target_pos_x, target_pos_y), duration=duration / 3)

            target_pos_x = pos[0] + (pos[0] - self.x) / 25
            target_pos_y = pos[1] + (pos[1] - self.y) / 25
            jump_anim = Animation(radius=self.radius * 1.2, duration=duration / 3, t='out_back')
            jump_anim &= Animation(pos=(target_pos_x, target_pos_y), duration=duration / 3)

            land_anim = Animation(radius=self.radius, duration=duration / 3, t='out_bounce')
            land_anim &= Animation(pos=pos, duration=duration / 3)

            anim = prep_anim + jump_anim + land_anim

        anim_scheduler.add(anim, self, context.move_info.order, lambda *args: self.on_finished_moving(context.end_coords, context.end_orientation))

    def move_to(self, hex_coords, tile_pos=None, trajectory=None):
        """ override from HexWidget """
        self.prepare_move()

        if trajectory:
            duration_per_tile = 0.2

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

            previous = trajectory[-2] if len(trajectory) > 1 else self.hex_coords
            destination = trajectory[-1]
            anim_scheduler.add(anim, self, 0, lambda *args: self.on_finished_moving(destination, destination - previous))

        else:
            super(Piece, self).move_to(hex_coords, tile_pos, trajectory)

    def on_finished_moving(self, end_pos, orientation):
        self.change_status(Status.idle)
        self.hex_coords = end_pos
        self.contour.show()
        self.unit.move_to(hex_coords=self.hex_coords, orientation=orientation)

    @check_root_window
    def on_pos(self, *args):
        self.contour.pos = self.pos
        for shape_part, offset in self.shape_parts.items():
            shape_part.pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])

        for shield_data in self.shields:
            for shield_part, (dx, dy, __) in shield_data.items():
                shield_part.pos = (self.pos[0] + dx, self.pos[1] + dy)

    @check_root_window
    def on_radius(self, *args):
        for shape_part, offset in self.shape_parts.items():
            shape_part.radius = self.radius

        for shield_data in self.shields:
            for shield_part, (dx, dy, i) in shield_data.items():
                shield_part.thickness = self.get_shield_thickness()
                shield_part.radius = self.get_shield_radius(i)

    @check_root_window
    def on_color_change(self, r, g, b, a):
        for shape_part, _ in self.shape_parts.items():
            shape_part.color = (r, g, b, a)

    def on_unit_health_change(self, health_change, context):
        duration = 0.2
        anim = None

        if health_change < 0:
            pt = self.hex_layout.hex_to_pixel(self.hex_coords + context.direction)
            target_pos_x = self.x + (pt.x - self.x) / 10
            target_pos_y = self.y + (pt.y - self.y) / 10
            anim = Animation(pos=(target_pos_x, target_pos_y), duration=duration / 3, **c_hit.rgb_dict)
            anim += Animation(pos=(self.x, self.y), r=self.r, g=self.g, b=self.b, duration=duration * 2 / 3)
        else:
            anim = Animation(radius=self.radius * 1.2, duration=duration / 3., **c_heal.rgb_dict)
            anim += Animation(radius=self.radius, r=self.r, g=self.g, b=self.b, duration=duration * 2 / 3)

        anim_scheduler.add(anim, self, context.hit.order)

        for target, target_type in context.targets_killed:
            if self.unit == target:
                anim = Animation(a=0, duration=duration)
                anim_scheduler.add(anim, self, 99)
                break

    def on_unit_targeted(self):
        duration = 3
        anim = Animation(**c_hit.rgb_dict, duration=duration / 3)
        anim += Animation(r=self.r, g=self.g, b=self.b, duration=duration * 2 / 3)
        anim.repeat = True
        anim.start(self)

    def on_targeted_end(self, shield_index=None):
        if shield_index is not None:
            self._on_targeted_end_shields(shield_index)
        else:
            Animation.cancel_all(self)
            self.color = self.unit.color

    def hex_test(self, hex_coords):
        return self.unit.hex_test(hex_coords)

#    ######  ##    ## #### ##       ##        ######
#   ##    ## ##   ##   ##  ##       ##       ##    ##
#   ##       ##  ##    ##  ##       ##       ##
#    ######  #####     ##  ##       ##        ######
#         ## ##  ##    ##  ##       ##             ##
#   ##    ## ##   ##   ##  ##       ##       ##    ##
#    ######  ##    ## #### ######## ########  ######
#   #################################################

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
            reachable_hexes = game_instance.battle.board.get_reachable(self.unit)
            for h in reachable_hexes:
                tile = Tile(q=h.q, r=h.r,
                            layout=self.hex_layout,
                            color=c_reachable_selected if self.selected else c_reachable_not_selected,
                            radius=self.radius - 2,
                            size=(self.radius - 2, self.radius - 2))
                self.parent.add_widget(tile)
                self.reachable_tiles.append(tile)

    def clean_reachable_tiles(self):
        for tile in self.reachable_tiles:
            self.parent.remove_widget(tile)
        self.reachable_tiles = []

    def is_in_move_range(self, hex_coords):
        if self.reachable_tiles:
            for tile in self.reachable_tiles:
                if tile.hex_coords == hex_coords:
                    return True
        return False

    def on_action_selected(self, action_type, rk_skill):
        self.clean_skill()
        if action_type == ActionType.move:
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
            self.selected = select
            if select:
                self.display_reachable_tiles()
                self.contour.show()
            else:
                self.clean_skill()
                self.clean_reachable_tiles()
                self.contour.hide()
