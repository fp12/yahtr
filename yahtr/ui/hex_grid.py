from kivy.uix.scatterlayout import ScatterLayout

from yahtr.ui.tile import Tile

from yahtr.core.hex_lib import Layout

from yahtr.game import game_instance
from yahtr.game_data import game_data


class HexGrid(ScatterLayout):
    hex_radius = 60
    hex_margin = 3

    def __init__(self, **kwargs):
        super(HexGrid, self).__init__(**kwargs)
        self.tiles = []
        self.hex_layout = Layout(origin=self.center, size=self.hex_radius, flat=game_instance.flat_layout, margin=self.hex_margin)
        self.load_grid()

    def load_grid(self):
        board_template = game_data.get_board_template('editor_default')
        for h in board_template.tiles:
            tile = Tile(line_rgba=(1, 1, 1, 1), q=h.q, r=h.r, layout=self.hex_layout, color=(0, 0, 0, 0), size=(self.hex_radius, self.hex_radius))
            self.add_widget(tile)
            self.tiles.append(tile)
