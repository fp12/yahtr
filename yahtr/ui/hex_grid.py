from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import NumericProperty, ObjectProperty

from yahtr.ui.tile import Tile

from yahtr.core import pathfinding
from yahtr.core.hex_lib import Layout, Hex

from yahtr.game import game_instance


class HexGrid(ScatterLayout):
    hex_radius = NumericProperty(40)
    hex_margin = NumericProperty(2)
    selector = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HexGrid, self).__init__(**kwargs)
        self.hex_layout = None
        self.content_hexes = []
        self.grid_hexes = set()
        self.tiles = []
        self.load_grid()

    def load_grid(self, content_hexes=None):
        self.unload_grid()
        if content_hexes:
            self.content_hexes = content_hexes
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)

        if len(self.content_hexes) == 0:
            self.grid_hexes.add(Hex(0, 0))
        else:
            for h in self.content_hexes:
                tile = self.create_content_tile(h)
                self.add_widget(tile)
                self.tiles.append(tile)
                self.grid_hexes.update(self.get_close_grid_tiles(h))

        for h in self.grid_hexes:
            tile = self.create_grid_tile(h)
            self.add_widget(tile)
            self.tiles.append(tile)

    def unload_grid(self):
        for t in self.tiles:
            self.remove_widget(t)
        self.tiles = []
        self.grid_hexes = set()
        self.hex_layout = None

    def on_hex_radius(self, instance, value):
        self.load_grid()

    def get_tile_on_hex(self, hex_coords):
        for tile in self.tiles:
            if tile.hex_coords == hex_coords:
                return tile
        return None

    def on_mouse_pos(self, *args):
        local_pos = self.to_local(*args[1])
        hover_hex = self.hex_layout.pixel_to_hex(local_pos)
        if not self.selector.hidden and self.selector.hex_coords == hover_hex:
            return False

        tile = self.get_tile_on_hex(hover_hex)
        if tile:
            self.selector.move_to(hover_hex, tile_pos=tile.pos)
            self.selector.show()
            return True

        self.selector.hide()
        return False

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

        if not self.selector.hidden:
            h = self.selector.hex_coords

            tile = self.get_tile_on_hex(h)
            # remove the tile first
            self.tiles.remove(tile)
            self.remove_widget(tile)

            if h in self.content_hexes:
                self.content_hexes.remove(h)
                self.grid_hexes.add(h)

                tile = self.create_grid_tile(h)
                self.add_widget(tile)
                self.tiles.append(tile)

            elif h in self.grid_hexes:
                self.content_hexes.append(h)
                self.grid_hexes.discard(h)

                tile = self.create_content_tile(h)
                self.add_widget(tile)
                self.tiles.append(tile)

                new_grid = self.get_close_grid_tiles(h)

                for h in new_grid:
                    if h not in self.grid_hexes:
                        self.grid_hexes.add(h)

                        tile = self.create_grid_tile(h)
                        self.add_widget(tile)
                        self.tiles.append(tile)

    def create_content_tile(self, h: Hex) -> Tile:
        return Tile(line_rgba=(0, 0, 0, 0), q=h.q, r=h.r, layout=self.hex_layout, color=(1, 1, 1, 1), size=(self.hex_radius, self.hex_radius))

    def create_grid_tile(self, h: Hex) -> Tile:
        return Tile(line_rgba=(0.7, 0.7, 0.7, 1), q=h.q, r=h.r, layout=self.hex_layout, color=(0, 0, 0, 0), size=(self.hex_radius, self.hex_radius))

    def get_close_grid_tiles(self, h: Hex):
        def get_cost(h: Hex):
            return 1

        def get_neighbours(h: Hex):
            for neighbour in h.get_neighbours():
                if neighbour not in self.content_hexes:
                    yield neighbour

        return pathfinding.Reachable(h, 2, get_neighbours, get_cost).get()
