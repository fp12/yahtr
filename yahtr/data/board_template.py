from enum import Enum

from yahtr.core.hex_lib import Hex
from yahtr.utils import attr
from yahtr.data.core import DataTemplate
from yahtr.data.board_creator import build_parallelogram, build_triangle, build_hexagon, build_rectangle
from yahtr.wall import Wall


class BoardType(Enum):
    custom = 0
    parallelogram = 1
    triangle = 2
    hexagon = 3
    rectangle = 4


class BoardTemplate(DataTemplate):
    """ Board as defined in data """

    __path = 'data/boards/'
    __ext = '.json'

    __attributes = ['info']
    __creators = {
            BoardType.parallelogram: build_parallelogram,
            BoardType.triangle: build_triangle,
            BoardType.hexagon: build_hexagon,
            BoardType.rectangle: build_rectangle
        }

    def __init__(self, file, data):
        self.id = file
        attr.get_from_dict(self, data, *BoardTemplate.__attributes)
        self.type = BoardType[data['type']]
        self.holes = [Hex(*qr) for qr in data['holes']] if 'holes' in data else []
        self.tiles = [Hex(*qr) for qr in data['adds']] if 'adds' in data else []
        self.walls = [Wall(d) for d in data['walls']] if 'walls' in data else []

        # call the appropriate creator
        BoardTemplate.__creators[self.type](self.tiles, self.holes, **self.info)

    def save(self):
        return {
            'type': self.type.name,
            'info': self.info,
            'holes': [[h.q, h.r] for h in self.holes],
            'adds': [[h.q, h.r] for h in self.tiles],
            'walls': [w.save() for w in self.walls],
        }

    @staticmethod
    def load_all():
        raw_data = DataTemplate.local_load(BoardTemplate.__path, BoardTemplate.__ext)
        return [BoardTemplate(file, data) for file, data in raw_data.items()]

    @staticmethod
    def load_one(board_id):
        data = DataTemplate.local_load_single(BoardTemplate.__path, board_id, BoardTemplate.__ext)
        if data:
            return BoardTemplate(board_id, data)
        return None

    @staticmethod
    def save_one(board_template):
        DataTemplate.local_save_single(BoardTemplate.__path, board_template.id, BoardTemplate.__ext, board_template.save())
