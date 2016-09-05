from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window

from hex_lib import Layout
import pathfinding
from game import game_instance
from ui.tile import Tile
from ui.unit import Unit, Status
from ui.selector import Selector
from ui.trajectory import Trajectory


class GameView(ScatterLayout):
    hex_radius = 30
    hex_margin = 2

    def __init__(self, **kwargs):
        super(GameView, self).__init__(**kwargs)
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)
        self._unit = None
        self.units = []
        self.tiles = []

        self.selector = Selector(q=5000, r=5000, layout=self.hex_layout, margin=2.5, color=[0.560784, 0.737255, 0.560784, 0.5])
        self.trajectory = Trajectory(color=[0, 0.392157, 0, 0.5])

        Window.bind(mouse_pos=self.on_mouse_pos)

    def spawn_unit(self, selected_class):
        if self._unit:
            self._unit.clear()
            self.remove_widget(self._unit)
        self._unit = Unit(template=game_instance.classes[selected_class], q=0, r=0, layout=self.hex_layout)
        self.add_widget(self._unit)
        self._unit.load()

    def load_map(self):
        for q, r in game_instance.current_fight.current_map.get_tiles():
            tile = Tile(q, r, layout=self.hex_layout, color=[0.8, 0.8, 0.8, 1], size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)
        self.add_widget(self.selector)
        self.add_widget(self.trajectory)

    def load_squads(self):
        for player, units in game_instance.current_fight.squads.items():
            for template_name, hex_coords in units.items():
                new_unit = Unit(template=game_instance.classes[template_name], q=hex_coords[0], r=hex_coords[1], layout=self.hex_layout)
                self.add_widget(new_unit)
                self.units.append(new_unit)
                new_unit.load()

    def on_debug_key(self):
        for x in self.tiles:
            x.toggle_debug_label()

    def get_tile_on_hex(self, hex_coords):
        for tile in self.tiles:
            if tile.hex_coords == hex_coords:
                return tile
        return None

    def get_unit_on_hex(self, hex_coords):
        for unit in self.units:
            if unit.hex_coords == hex_coords:
                return unit
        return None

    def get_selected_unit(self):
        for unit in self.units:
            if unit.selected:
                return unit

    def is_unit_moving(self):
        for unit in self.units:
            if unit.status == Status.Moving:
                return True
        return False

    def on_unit_move_end(self, unit):
        unit_hovered = self.get_unit_on_hex(self.selector.hex_coords)
        if unit == unit_hovered:
            unit_hovered.on_hovered_in()

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
                old_unit_hovered = self.get_unit_on_hex(self.selector.hex_coords)
                new_unit_hovered = self.get_unit_on_hex(hover_hex)
                if old_unit_hovered != new_unit_hovered:
                    if old_unit_hovered:
                        old_unit_hovered.on_hovered_out()
                    if new_unit_hovered:
                        new_unit_hovered.on_hovered_in()

                unit_selected = self.get_selected_unit()
                # unit is moving: clean everything
                if self.is_unit_moving() or new_unit_hovered:
                    self.trajectory.hide()
                # over tile with unit selected: show trajectory
                elif unit_selected:
                    path = pathfinding.get_best_path(game_instance.current_fight.current_map, unit_selected.hex_coords, hover_hex)
                    if path:
                        points = []
                        for hex_coords in path:
                            pt = self.hex_layout.hex_to_pixel(hex_coords)
                            points.append(pt.x)
                            points.append(pt.y)
                        if unit_selected.is_in_move_range(hover_hex):
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
        unit_touched = self.get_unit_on_hex(self.selector.hex_coords)
        unit_selected = self.get_selected_unit()
        if unit_touched and not unit_selected:
            return unit_touched.on_touched_down()
        elif not unit_touched:
            tile_touched = self.get_tile_on_hex(self.selector.hex_coords)
            if unit_selected and tile_touched and unit_selected.is_in_move_range(self.selector.hex_coords):
                self.trajectory.hide()
                unit_selected.move_to(self.selector.hex_coords, trajectory=self.trajectory.hex_coords, on_move_end=self.on_unit_move_end)
            return True
