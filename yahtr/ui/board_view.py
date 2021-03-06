from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock

from yahtr.ui.tile import Tile
from yahtr.ui.piece import Piece, Status
from yahtr.ui.selector import Selector
from yahtr.ui.trajectory import Trajectory
from yahtr.ui.wall_widget import WallWidget
from yahtr.ui.utils.reachable_pool import reachable_pool, ReachableType
from yahtr.ui.game_options import ReachableToggleType, SelectedReachableMode, OthersReachableMode

from yahtr.core.hex_lib import Layout
from yahtr.game import game_instance
from yahtr.data.actions import ActionType
from yahtr.utils import Color
from yahtr.utils.log import create_ui_logger
from yahtr.utils.event import Event
from yahtr.tie import TieType


logger = create_ui_logger('BoardView')


class BoardView(ScatterLayout):
    hex_radius = 60
    hex_margin = 3
    trajectory_color_ok = Color(10, 214, 126, 255)
    tile_color = Color(82, 82, 82, 255)
    selector_color = Color.darkseagreen

    def __init__(self, **kwargs):
        super(BoardView, self).__init__(**kwargs)
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)
        self.pieces = []
        self.tiles = []
        self.walls = []
        self.reachables_layer = Widget()
        self.selector = Selector(q=0, r=0, layout=self.hex_layout, margin=2.5, color=self.selector_color)
        self.trajectory = Trajectory()
        self.current_action = None
        self.attach_event = None  # kivy.Clock event used every frame when attached to a piece is moving

        self.reachable_modes = (SelectedReachableMode.on, OthersReachableMode.none)

        self.on_unit_hovered = Event('unit', 'hovered_in')

    def load_board(self):
        for h in game_instance.battle.board.tiles:
            tile = Tile(q=h.q, r=h.r, layout=self.hex_layout, color=self.tile_color, size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)

        for w in game_instance.battle.board.walls:
            pos = self.hex_layout.get_mid_edge_position(w.origin, w.destination)
            angle = w.origin.angle_to_neighbour(w.destination - w.origin)
            wall = WallWidget(w, pos=pos.tup, angle=angle, size=(self.hex_radius * 7. / 9., self.hex_margin * 0.9))
            self.add_widget(wall)
            self.walls.append(wall)

        self.add_widget(self.reachables_layer)
        reachable_pool.setup(self.hex_layout, self.reachables_layer)

        game_instance.battle.board.on_wall_hit += self.on_wall_hit
        game_instance.battle.board.on_wall_targeted += self.on_wall_targeted
        game_instance.battle.board.on_unit_removed += self.on_unit_removed

        self.add_widget(self.selector)
        self.add_widget(self.trajectory)

    def load_squads(self):
        for player, squad in game_instance.battle.squads.items():
            for unit in squad:
                new_piece = Piece(unit=unit, layout=self.hex_layout)
                self.add_widget(new_piece)
                self.pieces.append(new_piece)
                new_piece.load()
        game_instance.battle.on_select_action += self.on_action_selected
        game_instance.battle.on_new_turn += self.on_new_turn

    def on_unit_removed(self, unit):
        for piece in self.pieces:
            if piece.unit == unit:
                self.clean_reachable_tiles(piece)
                piece.unload()
                self.remove_widget(piece)
                self.pieces.remove(piece)
                return

    def on_debug_key(self, keycode, code):
        for x in self.tiles:
            x.toggle_debug_label()

    def on_center_key(self, keycode, code):
        selected_piece = self.get_selected_piece()
        if selected_piece:
            self.center_game_view(selected_piece.pos, 0.1)

    def on_action_selected(self, unit, action_type, rk_skill):
        self.current_action = action_type
        piece = self.get_selected_piece()
        if piece:
            piece.on_action_selected(action_type, rk_skill)
            if action_type is ActionType.move:
                self.reset_reachables(ReachableToggleType.selected)
            else:
                self.clean_reachable_tiles(piece)
            piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
            if action_type is ActionType.move and piece and not piece_hovered:
                self.display_trajectory(piece, self.selector.hex_coords)
                return
        self.trajectory.hide()

    def display_trajectory(self, piece, hover_hex):
        path = game_instance.battle.board.get_best_path(piece.unit, hover_hex)
        if path:
            points = []
            for hex_coords in path:
                pt = self.hex_layout.hex_to_pixel(hex_coords)
                points.append(pt.x)
                points.append(pt.y)
            if hover_hex in piece.unit.reachables:
                self.trajectory.color = self.trajectory_color_ok
            self.trajectory.set(path, points)

    def get_tile_on_hex(self, hex_coords):
        for tile in self.tiles:
            if tile.hex_coords == hex_coords:
                return tile
        return None

    def get_piece_on_hex(self, hex_coords):
        for piece in self.pieces:
            if piece.hex_test(hex_coords):
                return piece
        return None

    def get_piece_for_unit(self, unit):
        for piece in self.pieces:
            if piece.unit == unit:
                return piece
        return None

    def get_selected_piece(self):
        for piece in self.pieces:
            if piece.selected:
                return piece
        return None

    def center_game_view(self, pos, duration=0.7):
        scaled_pos = [pos[0] * self.scale, pos[1] * self.scale]
        end_pos = [self.hex_layout.origin.x - scaled_pos[0], self.hex_layout.origin.y - scaled_pos[1]]
        Animation.cancel_all(self)
        if duration > 0:
            anim = Animation(pos=end_pos, duration=duration)
            anim.start(self)
        else:
            self.pos = end_pos

    def on_new_turn(self, unit):
        self.trajectory.hide()
        new_selected_piece = None

        for piece in self.pieces:
            if piece.unit == unit:
                new_selected_piece = piece
            elif piece.selected:
                piece.do_select(False)
                piece.on_status_change -= self.on_piece_status_change

        if new_selected_piece:
            new_selected_piece.do_select(True)
            new_selected_piece.on_status_change += self.on_piece_status_change
            self.center_game_view(new_selected_piece.pos)

        self.reset_reachables(ReachableToggleType.selected)
        self.reset_reachables(ReachableToggleType.others)

    def on_piece_attached(self, dt):
        selected_piece = self.get_selected_piece()
        self.center_game_view(selected_piece.pos, duration=0)

    def on_piece_status_change(self, piece, new_status):
        if new_status == Status.moving:
            self.trajectory.hide()
            self.clean_reachable_tiles(piece)
            if self.attach_event:
                self.attach_event.cancel()
            self.attach_event = Clock.schedule_interval(self.on_piece_attached, 0.016667)  # 1 / 60

        elif new_status == Status.idle and self.attach_event:
            self.attach_event.cancel()
            game_instance.battle.clean_all_reachables()
            self.reset_reachables(ReachableToggleType.selected)

    def process_piece_hovered(self, piece, hovered_in):
        if hovered_in:
            piece.on_hovered_in()

            if piece.selected:
                if self.reachable_modes[0] == SelectedReachableMode.off:
                    self.display_reachable_tiles(piece)
            else:
                tie = game_instance.battle.get_tie_with_selected_unit(piece.unit)
                if tie == TieType.ally and self.reachable_modes[1] in (OthersReachableMode.none, OthersReachableMode.ennemies):
                    self.display_reachable_tiles(piece)
                elif tie == TieType.enemy and self.reachable_modes[1] in (OthersReachableMode.none, OthersReachableMode.allies):
                    self.display_reachable_tiles(piece)
        else:
            piece.on_hovered_out()

            if piece.selected:
                if self.reachable_modes[0] == SelectedReachableMode.off:
                    piece.clean_reachable_tiles()
            else:
                tie = game_instance.battle.get_tie_with_selected_unit(piece.unit)
                if tie == TieType.ally and self.reachable_modes[1] in (OthersReachableMode.none, OthersReachableMode.ennemies):
                    self.clean_reachable_tiles(piece)
                elif tie == TieType.enemy and self.reachable_modes[1] in (OthersReachableMode.none, OthersReachableMode.allies):
                    self.clean_reachable_tiles(piece)

    def display_reachable_tiles(self, piece):
        reachable_type = ReachableType.selected_unit
        if not piece.selected:
            tie = game_instance.battle.get_tie_with_selected_unit(piece.unit)
            reachable_type = ReachableType.ally_unit if tie == TieType.ally else ReachableType.ennemy_unit
        piece.unit.reachables = reachable_pool.request_reachables(piece.unit, reachable_type)

    def clean_reachable_tiles(self, piece):
        reachable_pool.release_reachables(piece.unit)

    def reset_reachables(self, what):
        if what is ReachableToggleType.selected:
            selected_piece = self.get_selected_piece()
            if self.reachable_modes[0] == SelectedReachableMode.on:
                self.display_reachable_tiles(selected_piece)
            else:
                self.clean_reachable_tiles(selected_piece)
        else:
            mode = self.reachable_modes[1]
            for piece in self.pieces:
                if piece.selected:
                    continue
                if mode == OthersReachableMode.none:
                    self.clean_reachable_tiles(piece)
                    continue
                tie = game_instance.battle.get_tie_with_selected_unit(piece.unit)
                if tie == TieType.ally:
                    if mode is OthersReachableMode.ennemies:
                        self.clean_reachable_tiles(piece)
                    else:
                        self.display_reachable_tiles(piece)
                else:
                    if mode is OthersReachableMode.allies:
                        self.clean_reachable_tiles(piece)
                    else:
                        self.display_reachable_tiles(piece)

    def on_unit_hovered_external(self, unit, hovered_in):
        piece = self.get_piece_for_unit(unit)
        if piece:
            self.process_piece_hovered(piece, hovered_in)
            if hovered_in:
                tile = self.get_tile_on_hex(piece.hex_coords)
                self.selector.move_to(piece.hex_coords, tile_pos=tile.pos)
                self.selector.show()

    def on_toggle_reachables(self, what, mode):
        if what is ReachableToggleType.selected:
            self.reachable_modes = (mode, self.reachable_modes[1])
        else:
            self.reachable_modes = (self.reachable_modes[0], mode)
        self.reset_reachables(what)

    def on_wall_hit(self, origin, destination, destroyed):
        for w in self.walls:
            if w.origin == origin and w.destination == destination or w.origin == destination and w.destination == origin:
                if destroyed:
                    self.remove_widget(w)
                    self.walls.remove(w)
                return

    def on_wall_targeted(self, wall, targeted):
        for w in self.walls:
            if w.origin == wall.origin and w.destination == wall.destination or w.origin == wall.destination and w.destination == wall.origin:
                if targeted:
                    duration = 3
                    anim = Animation(**Color.firebrick.rgb_dict, duration=duration / 3)
                    anim += Animation(r=w.r, g=w.g, b=w.b, duration=duration * 2 / 3)
                    anim.repeat = True
                    anim.start(w)
                else:
                    Animation.cancel_all(w)
                    w.color = w.get_default_color()
                return

    def on_mouse_pos(self, *args):
        local_pos = self.to_local(*args[1])
        hover_hex = self.hex_layout.pixel_to_hex(local_pos)
        if not self.selector.hidden and self.selector.hex_coords == hover_hex:
            return False

        tile = self.get_tile_on_hex(hover_hex)
        if tile:
            old_piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
            new_piece_hovered = self.get_piece_on_hex(hover_hex)
            if old_piece_hovered != new_piece_hovered:
                if old_piece_hovered:
                    self.process_piece_hovered(old_piece_hovered, False)
                    self.on_unit_hovered(old_piece_hovered.unit, False)
                if new_piece_hovered:
                    self.process_piece_hovered(new_piece_hovered, True)
                    self.on_unit_hovered(new_piece_hovered.unit, True)

            piece_selected = self.get_selected_piece()
            if piece_selected:
                if self.current_action is ActionType.move:
                    if piece_selected.status == Status.moving or new_piece_hovered:
                        self.trajectory.hide()
                    else:
                        orientation = None
                        if hover_hex in piece_selected.unit.reachables:
                            self.display_trajectory(piece_selected, hover_hex)
                            if len(self.trajectory.steps) > 1:
                                orientation = piece_selected.hex_coords.direction_to_distant(self.trajectory.steps[-2])
                        else:
                            self.trajectory.hide()
                            orientation = piece_selected.hex_coords.direction_to_distant(hover_hex)
                        if orientation:
                            piece_selected.unit.move_to(orientation=orientation)
                            piece_selected.do_rotate()

                elif self.current_action in [ActionType.rotate, ActionType.weapon, ActionType.skill] and piece_selected.hex_coords != hover_hex:
                    orientation = piece_selected.hex_coords.direction_to_distant(hover_hex)
                    if orientation != piece_selected.unit.orientation and game_instance.battle.board.unit_can_fit(piece_selected.unit, piece_selected.unit.hex_coords, orientation):
                        self.clean_reachable_tiles(piece_selected)
                        piece_selected.unit.move_to(orientation=orientation)
                        piece_selected.do_rotate()
                        game_instance.battle.notify_action_validation(self.current_action, piece_selected.current_skill)

            # finally move the selector
            self.selector.move_to(hover_hex, tile_pos=tile.pos)
            self.selector.show()
            return True

        self.selector.hide()
        self.on_no_mouse_pos()
        return False

    def on_no_mouse_pos(self):
        self.trajectory.hide()

    def on_touch_down(self, touch):
        if not touch.is_mouse_scrolling:
            touch.grab(self)
            touch.ud['frame_count'] = 1

    def on_touch_up(self, touch):
        if touch.is_mouse_scrolling:
            return

        if touch.grab_current is self:
            touch.ungrab(self)
            return

        if 'frame_count' in touch.ud and touch.ud['frame_count'] > 2:
            return

        piece_selected = self.get_selected_piece()
        if piece_selected and self.current_action in [ActionType.rotate, ActionType.weapon, ActionType.skill]:
            game_instance.battle.notify_action_end(self.current_action, rk_skill=piece_selected.current_skill)
            self.current_action = None
            piece_selected.clean_skill()
            return True

        piece_touched = self.get_piece_on_hex(self.selector.hex_coords)
        if piece_touched and not piece_selected:
            return piece_touched.on_touched_down()

        if not piece_touched and piece_selected and self.current_action is ActionType.move:
            tile_touched = self.get_tile_on_hex(self.selector.hex_coords)
            if tile_touched and self.selector.hex_coords in piece_selected.unit.reachables:
                self.trajectory.hide()
                game_instance.battle.notify_action_end(ActionType.move, trajectory=self.trajectory.steps)
                self.current_action = None
                return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super(BoardView, self).on_touch_move(touch)

        touch.ud['frame_count'] += 1
        self.x += touch.dx
        self.y += touch.dy

    def zoom(self, value):
        new_scale = self.scale + value
        if 0.1 <= new_scale <= 1.5:
            rescale = new_scale * 1.0 / self.scale
            self.apply_transform(Matrix().scale(rescale, rescale, rescale),
                                 post_multiply=True,
                                 anchor=self.to_local(*self.hex_layout.origin.tup))  # == window center

    def on_zoom_up(self, *args):
        self.zoom(-0.1)

    def on_zoom_down(self, *args):
        self.zoom(0.1)

    def on_move_key(self, keycode, code):
        move = 25
        if code == 'a':
            self.x += move
        if code == 'd':
            self.x -= move
        if code == 'w':
            self.y -= move
        if code == 's':
            self.y += move
