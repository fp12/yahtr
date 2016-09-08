from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window

from ui.tile import Tile
from ui.piece import Piece, Status
from ui.selector import Selector
from ui.trajectory import Trajectory

from hex_lib import Layout
import pathfinding
from game import game_instance


class GameView(ScatterLayout):
    hex_radius = 40
    hex_margin = 2

    def __init__(self, **kwargs):
        super(GameView, self).__init__(**kwargs)
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)
        self.piece = None
        self.pieces = []
        self.tiles = []
        self.selector = Selector(q=5000, r=5000, layout=self.hex_layout, margin=2.5, color=[0.560784, 0.737255, 0.560784, 0.5])
        self.trajectory = Trajectory(color=[0, 0.392157, 0, 0.5])

        Window.bind(mouse_pos=self.on_mouse_pos)

    def spawn_piece(self, template):
        if self.piece:
            self.piece.clear()
            self.remove_widget(self.piece)
        self.piece = Piece(template=game_instance.classes[template], q=0, r=0, layout=self.hex_layout)
        self.add_widget(self.piece)
        self.piece.load()

    def load_map(self):
        for q, r in game_instance.current_fight.current_map.get_tiles():
            tile = Tile(q, r, layout=self.hex_layout, color=[0.8, 0.8, 0.8, 0.4], size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)
        self.add_widget(self.selector)
        self.add_widget(self.trajectory)

    def load_squads(self):
        for player, squad in game_instance.current_fight.squads.items():
            for unit in squad:
                new_piece = Piece(unit=unit, layout=self.hex_layout)
                self.add_widget(new_piece)
                self.pieces.append(new_piece)
                new_piece.load()
        self.select_piece_for_turn()

    def on_debug_key(self):
        for x in self.tiles:
            x.toggle_debug_label()

    def on_action_change(self, action_type):
        piece = self.get_selected_piece()
        if piece:
            piece.on_action_change(action_type)

    def get_tile_on_hex(self, hex_coords):
        for tile in self.tiles:
            if tile.hex_coords == hex_coords:
                return tile
        return None

    def get_piece_on_hex(self, hex_coords):
        for piece in self.pieces:
            if piece.hex_coords == hex_coords:
                return piece
        return None

    def get_selected_piece(self):
        for piece in self.pieces:
            if piece.selected:
                return piece

    def is_piece_moving(self):
        for piece in self.pieces:
            if piece.status == Status.Moving:
                return True
        return False

    def select_piece_for_turn(self):
        _, _, unit = game_instance.current_fight.time_bar.current
        for piece in self.pieces:
            if piece.unit == unit:
                piece.select_for_turn()

    def on_piece_move_end(self, piece):
        _, _, unit = game_instance.current_fight.time_bar.next()
        for piece in self.pieces:
            if piece.unit == unit:
                piece.select_for_turn()
        piece_hovered = self.get_piece_on_hex(self.selector.hex_coords)
        if piece == piece_hovered:
            piece_hovered.on_hovered_in()

    def on_mouse_pos(self, stuff, pos):
        # do proceed if not displayed and/or no parent
        if not self.get_root_window():
            return

        # get rounded hex coordinates and do nothing if we didn't change hex
        hover_hex = self.hex_layout.pixel_to_hex(pos).get_round()
        if self.selector.hex_coords == hover_hex:
            return

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
                # piece is moving: clean everything
                if self.is_piece_moving() or new_piece_hovered:
                    self.trajectory.hide()
                # over tile with piece selected: show trajectory
                elif piece_selected:
                    path = pathfinding.get_best_path(game_instance.current_fight.current_map, piece_selected.hex_coords, hover_hex)
                    if path:
                        points = []
                        for hex_coords in path:
                            pt = self.hex_layout.hex_to_pixel(hex_coords)
                            points.append(pt.x)
                            points.append(pt.y)
                        if piece_selected.is_in_move_range(hover_hex):
                            self.trajectory.color = [0, 0.392157, 0, 0.5]
                        else:
                            self.trajectory.color = [0.9, 0.12, 0, 0.75]
                        self.trajectory.set(path, points)

            # finally move the selector
            self.selector.move_to(hover_hex, tile_pos=tile.pos)
            self.selector.hide(False)
            return True
        else:
            # if we aren't on a tile, we reset the selector and trajectory
            self.selector.hide()
            self.trajectory.hide()
            return False

    def on_touch_down(self, touch):
        piece_touched = self.get_piece_on_hex(self.selector.hex_coords)
        piece_selected = self.get_selected_piece()
        if piece_touched and not piece_selected:
            return piece_touched.on_touched_down()
        elif not piece_touched:
            tile_touched = self.get_tile_on_hex(self.selector.hex_coords)
            if piece_selected and tile_touched and piece_selected.is_in_move_range(self.selector.hex_coords):
                self.trajectory.hide()
                piece_selected.move_to(self.selector.hex_coords, trajectory=self.trajectory.steps, on_move_end=self.on_piece_move_end)
            return True
