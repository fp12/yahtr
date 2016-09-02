from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window

from hex_lib import Layout
import a_star
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
        self.tiles = []

        for q, r in game_instance.current_map.get_tiles():
            tile = Tile(q, r, layout=self.hex_layout, color=[0.8, 0.8, 0.8, 1], size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)

        self.selector = Selector(q=0, r=0, layout=self.hex_layout, margin=2.5, color=[0.560784, 0.737255, 0.560784, 0.5])
        self.selector.hide()
        self.add_widget(self.selector)

        self.trajectory = Trajectory(color=[0.360784, 0.437255, 0.860784, 0.5])
        self.trajectory.hide()
        self.add_widget(self.trajectory)

        Window.bind(mouse_pos=self.on_mouse_pos)

    def spawn_unit(self, selected_class):
        if self._unit:
            self._unit.clear()
            self.remove_widget(self._unit)
        self._unit = Unit(template=game_instance.classes[selected_class], q=0, r=0, layout=self.hex_layout)
        self.add_widget(self._unit)
        self._unit.load()

    def on_debug_key(self):
        for x in self.tiles:
            x.toggle_debug_label()

    def on_mouse_pos(self, stuff, pos):
        # do proceed if not displayed and/or no parent
        if not self.get_root_window():
            return
        # get rounded hex coordinates
        hover_hex = self.hex_layout.pixel_to_hex(pos).get_round()
        if self.selector.hex_coords == hover_hex:
            return
        for tile in self.tiles:
            if tile.hex_coords == hover_hex:
                self.selector.move_to(hover_hex, tile_pos=tile.pos)
                self.selector.hide(False)

                if self._unit:
                    if self._unit.status == Status.Moving or self._unit.hex_coords == tile.hex_coords:
                        self.trajectory.hide()
                        reachable_h = a_star.get_reachable(game_instance.current_map, self._unit.hex_coords, 4)
                        for x in reachable_h:
                            for x_tile in self.tiles:
                                if x_tile.hex_coords == x:
                                    x_tile.color = [1, 0, 1, 1]
                    else:
                        path = a_star.get_best_path(game_instance.current_map, self._unit.hex_coords, tile.hex_coords)
                        if path:
                            points = []
                            for hex_coords in path:
                                pt = self.hex_layout.hex_to_pixel(hex_coords)
                                points.append(pt.x)
                                points.append(pt.y)
                            self.trajectory.set(path, points)
                return True
        # if we aren't on a tile, we reset the selector and trajectory
        self.selector.hide()
        self.trajectory.hide()
        return False

    def on_touch_down(self, touch):
        if self._unit:
            if self.selector.hex_coords == self._unit.hex_coords:
                return self._unit.on_real_touch_down()
            else:
                self.trajectory.hide()
                self._unit.move_to(self.selector.hex_coords, trajectory=self.trajectory.hex_coords)
                return True