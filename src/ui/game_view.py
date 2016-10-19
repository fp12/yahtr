from kivy.uix.scatterlayout import ScatterLayout

from ui.tile import Tile
from ui.piece import Piece, Status
from ui.selector import Selector
from ui.trajectory import Trajectory
from ui.base_widgets import AngledColoredWidget
from ui.wall_widget import WallWidget

from hex_lib import Layout
from game import game_instance
from actions import ActionType
from utils import Color


class GameView(ScatterLayout):
    hex_radius = 40
    hex_margin = 2
    trajectory_color_ok = Color(0, 0.392157, 0, 0.85)
    trajectory_color_error = Color(0.9, 0.12, 0, 0.85)
    tile_color = Color(0.8, 0.8, 0.8, 0.4)
    selector_color = Color.darkseagreen

    def __init__(self, **kwargs):
        super(GameView, self).__init__(**kwargs)
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)
        self.piece = None
        self.pieces = []
        self.tiles = []
        self.walls = []
        self.selector = Selector(q=0, r=0, layout=self.hex_layout, margin=2.5, color=self.selector_color)
        self.trajectory = Trajectory(color=self.trajectory_color_ok)
        self.current_action = None

    def load_map(self):
        for q, r in game_instance.current_fight.current_map.get_tiles():
            tile = Tile(q, r, layout=self.hex_layout, color=self.tile_color, size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)

        for w in game_instance.current_fight.current_map.walls:
            pos = self.hex_layout.get_mid_edge_position(w.origin, w.destination)
            angle = w.origin.angle_to_neighbour(w.destination - w.origin)
            wall = WallWidget(w, pos=pos.tup, angle=angle, size=(self.hex_radius * 2 / 3., self.hex_margin * 3))
            self.add_widget(wall)
            self.walls.append(wall)

        game_instance.current_fight.current_map.on_wall_hit += self.on_wall_hit

        self.add_widget(self.selector)
        self.add_widget(self.trajectory)

    def load_squads(self):
        for player, squad in game_instance.current_fight.squads.items():
            for unit in squad:
                new_piece = Piece(unit=unit, layout=self.hex_layout)
                self.add_widget(new_piece)
                self.pieces.append(new_piece)
                new_piece.load()
        game_instance.current_fight.on_action_change += self.on_action_change
        game_instance.current_fight.on_next_turn += self.on_next_turn

    def on_debug_key(self, code, key):
        for x in self.tiles:
            x.toggle_debug_label()

    def on_action_change(self, unit, action_type, action_node, rk_skill):
        self.current_action = action_type
        piece = self.get_selected_piece()
        if piece:
            piece.on_action_change(action_type, rk_skill)
            piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
            if action_type == ActionType.Move and piece and not piece_hovered:
                self.display_trajectory(piece, self.selector.hex_coords)
                return
        self.trajectory.hide()

    def display_trajectory(self, piece, hover_hex):
        path = game_instance.current_fight.current_map.get_best_path(piece.hex_coords, hover_hex)
        if path:
            points = []
            for hex_coords in path:
                pt = self.hex_layout.hex_to_pixel(hex_coords)
                points.append(pt.x)
                points.append(pt.y)
            if piece.is_in_move_range(hover_hex):
                self.trajectory.color = self.trajectory_color_ok
            else:
                self.trajectory.color = self.trajectory_color_error
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

    def get_selected_piece(self):
        for piece in self.pieces:
            if piece.selected:
                return piece

    def on_next_turn(self, unit):
        self.trajectory.hide()
        for piece in self.pieces:
            if piece.unit == unit:
                piece.do_select(True)
            elif piece.selected:
                piece.do_select(False)

    def on_piece_move_end(self, piece):
        piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
        if piece == piece_hovered:
            piece_hovered.on_hovered_in()
        game_instance.current_fight.notify_action_end(ActionType.Move)

    def on_wall_hit(self, origin, destination, destroyed):
        for w in self.walls:
            if w.origin == origin and w.destination == destination or w.origin == destination and w.destination == origin:
                if destroyed:
                    self.remove_widget(w)
                    self.walls.remove(w)
                return

    def on_mouse_pos(self, *args):
        # get rounded hex coordinates and do nothing if we didn't change hex
        local_pos = self.to_local(*args[1])
        hover_hex = self.hex_layout.pixel_to_hex(local_pos).get_round()
        if not self.selector.hidden and self.selector.hex_coords == hover_hex:
            return False

        tile = self.get_tile_on_hex(hover_hex)
        if tile:
            if game_instance.current_fight and game_instance.current_fight.started:
                old_piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
                new_piece_hovered = self.get_piece_on_hex(hover_hex)
                if old_piece_hovered != new_piece_hovered:
                    if old_piece_hovered:
                        old_piece_hovered.on_hovered_out()
                    if new_piece_hovered:
                        new_piece_hovered.on_hovered_in()

                piece_selected = self.get_selected_piece()
                if piece_selected:
                    if self.current_action == ActionType.Move:
                        if piece_selected.status == Status.Moving or new_piece_hovered:
                            self.trajectory.hide()
                        else:
                            self.display_trajectory(piece_selected, hover_hex)
                            if self.trajectory and self.trajectory.steps:
                                orientation = piece_selected.hex_coords.direction_to_distant(self.trajectory.steps[-2])
                                piece_selected.unit.orientation = orientation
                                piece_selected.do_rotate()
                    elif self.current_action in [ActionType.Rotate, ActionType.Weapon, ActionType.Skill] and piece_selected.hex_coords != hover_hex:
                        orientation = piece_selected.hex_coords.direction_to_distant(hover_hex)
                        if game_instance.current_fight.current_map.unit_can_fit(piece_selected.unit, piece_selected.unit.hex_coords, orientation):
                            piece_selected.unit.orientation = orientation
                            piece_selected.do_rotate()

            # finally move the selector
            self.selector.move_to(hover_hex, tile_pos=tile.pos)
            self.selector.hide(False)
            return True

        self.on_no_mouse_pos()
        return False

    def on_no_mouse_pos(self):
        self.selector.hide()
        self.trajectory.hide()

    def on_touch_down(self, touch):
        ret = super(GameView, self).on_touch_down(touch)
        touch.ud['frame_count'] = 1
        return ret

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(GameView, self).on_touch_up(touch)

        if touch.ud['frame_count'] > 2:
            return

        piece_selected = self.get_selected_piece()
        if piece_selected and self.current_action in [ActionType.Rotate, ActionType.Weapon, ActionType.Skill]:
            game_instance.current_fight.notify_action_end(self.current_action, piece_selected.current_skill)
            piece_selected.clean_skill()
            return True

        piece_touched = self.get_piece_on_hex(self.selector.hex_coords)
        if piece_touched and not piece_selected:
            return piece_touched.on_touched_down()

        if not piece_touched:
            tile_touched = self.get_tile_on_hex(self.selector.hex_coords)
            if piece_selected and tile_touched and piece_selected.is_in_move_range(self.selector.hex_coords):
                self.trajectory.hide()
                piece_selected.move_to(self.selector.hex_coords, trajectory=self.trajectory.steps, on_move_end=self.on_piece_move_end)
                return True

        return super(GameView, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super(GameView, self).on_touch_move(touch)

        touch.ud['frame_count'] += 1
        self.x += touch.dx
        self.y += touch.dy
