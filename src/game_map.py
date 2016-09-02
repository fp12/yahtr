from enum import Enum
from math import floor

import data_loader


class MapType(Enum):
    Custom = 0
    Parallelogram = 1
    Triangle = 2
    Hexagon = 3
    Rectangle = 4


class Map():
    def __init__(self, name):
        self.name = name
        data = data_loader.local_load_single('data/maps/', name, '.json')

        # checks
        if data['type'] == MapType.Parallelogram.name:
            self._check_and_set('q1', data['info'])
            self._check_and_set('q2', data['info'])
            self._check_and_set('r1', data['info'])
            self._check_and_set('r2', data['info'])
            self.get_tiles = self._get_tiles_parallelogram
        elif data['type'] == MapType.Triangle.name:
            self._check_and_set('size', data['info'])
            self.get_tiles = self._get_tiles_triangle
        elif data['type'] == MapType.Hexagon.name:
            self._check_and_set('radius', data['info'])
            self.get_tiles = self._get_tiles_hexagon
        elif data['type'] == MapType.Rectangle.name:
            self._check_and_set('height', data['info'])
            self._check_and_set('width', data['info'])
            self.get_tiles = self._get_tiles_rectangle

        self.holes = data['holes'] if 'holes' in data else None

    def _check_and_set(self, var, info):
        assert(var in info)
        setattr(self, var, info[var])

    def validate_coords(self, q, r):
        if self.holes and [q, r] in self.holes:
            return False
        return True

    def _get_tiles_parallelogram(self):
        for q in range(self.q1, self.q2 + 1):
            for r in range(self.r1, self.r2 + 1):
                if self.validate_coords(q, r):
                    yield q, r

    def _get_tiles_triangle(self):
        for q in range(self.size + 1):
            for r in range(self.size - q, self.size + 1):
                if self.validate_coords(q, r):
                    yield q, r

    def _get_tiles_hexagon(self):
        for q in range(-self.radius, self.radius + 1):
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            for r in range(r1, r2 + 1):
                if self.validate_coords(q, r):
                    yield q, r

    def _get_tiles_rectangle(self):
        for r in range(self.height):
            r_offset = floor(r / 2.)
            for q in range(-r_offset, self.width - r_offset):
                if self.validate_coords(q, r):
                    yield q, r

    def get_neighbours(self, hex_coords):
        for neighbour in hex_coords.get_neighbours():
            if self.validate_coords(neighbour.q, neighbour.r):
                yield neighbour
