from enum import Enum
from math import floor

import data_loader
from hex_lib import Hex
from utils import attr
import pathfinding
import tie


class MapType(Enum):
    Custom = 0
    Parallelogram = 1
    Triangle = 2
    Hexagon = 3
    Rectangle = 4


class Map():
    def __init__(self, fight, name):
        self.fight = fight
        self.name = name
        data = data_loader.local_load_single('data/maps/', name, '.json')

        # checks
        if data['type'] == MapType.Parallelogram.name:
            attr.get_from_dic(self, data['info'], 'q1', 'q2', 'r1', 'r2')
            self.get_tiles = self._get_tiles_parallelogram
        elif data['type'] == MapType.Triangle.name:
            attr.get_from_dic(self, data['info'], 'size')
            self.get_tiles = self._get_tiles_triangle
        elif data['type'] == MapType.Hexagon.name:
            attr.get_from_dic(self, data['info'], 'radius')
            self.get_tiles = self._get_tiles_hexagon
        elif data['type'] == MapType.Rectangle.name:
            attr.get_from_dic(self, data['info'], 'height', 'width')
            self.get_tiles = self._get_tiles_rectangle

        self.holes = data['holes'] if 'holes' in data else None
        self.tiles = []  # lazy loaded
        self.units = []  # ref

    def register_units(self, units):
        self.units.extend(units)

    def _validate_not_hole(self, q, r):
        if self.holes and [q, r] in self.holes:
            return False
        return True

    def _get_tiles_parallelogram(self):
        if self.tiles:
            return self.tiles
        else:
            for q in range(self.q1, self.q2 + 1):
                for r in range(self.r1, self.r2 + 1):
                    if self._validate_not_hole(q, r):
                        self.tiles.append(Hex(q, r))
                        yield q, r

    def _get_tiles_triangle(self):
        if self.tiles:
            return self.tiles
        else:
            for q in range(self.size + 1):
                for r in range(self.size - q, self.size + 1):
                    if self._validate_not_hole(q, r):
                        self.tiles.append(Hex(q, r))
                        yield q, r

    def _get_tiles_hexagon(self):
        if self.tiles:
            return self.tiles
        else:
            for q in range(-self.radius, self.radius + 1):
                r1 = max(-self.radius, -q - self.radius)
                r2 = min(self.radius, -q + self.radius)
                for r in range(r1, r2 + 1):
                    if self._validate_not_hole(q, r):
                        self.tiles.append(Hex(q, r))
                        yield q, r

    def _get_tiles_rectangle(self):
        if self.tiles:
            return self.tiles
        else:
            for r in range(self.height):
                r_offset = floor(r / 2.)
                for q in range(-r_offset, self.width - r_offset):
                    if self._validate_not_hole(q, r):
                        self.tiles.append(Hex(q, r))
                        yield q, r

    def get_unit_on(self, hex_coords, include_shape=True):
        for u in self.units:
            if u.hex_coords == hex_coords:
                return u
            if include_shape and hex_coords in u.current_shape:
                return u
        return None

    def get_free_neighbours(self, unit, hex_coords):
        units_hexes = []
        for u in self.units:
            if u != unit:
                units_hexes.extend(u.current_shape)
        for neighbour in hex_coords.get_neighbours():
            orientation = neighbour - hex_coords
            shape_can_fit = True
            for shape_part in unit.calc_shape_at(neighbour, orientation):
                if shape_part not in self.tiles or shape_part in units_hexes:
                    shape_can_fit = False
                    break
            if shape_can_fit:
                yield neighbour

    def unit_can_fit(self, unit, hex_coords, orientation):
        units_hexes = []
        for u in self.units:
            if u != unit:
                units_hexes.extend(u.current_shape)
        for shape_part in unit.calc_shape_at(hex_coords, orientation):
            if shape_part not in self.tiles or shape_part in units_hexes:
                return False
        return True

    def get_all_neighbours(self, hex_coords):
        for neighbour in hex_coords.get_neighbours():
            if neighbour in self.tiles:
                yield neighbour

    def _get_cost(self, unit, a):
        for n in self.get_all_neighbours(a):
            other_unit = self.get_unit_on(n)
            if other_unit and self.fight.get_tie(unit.owner, other_unit.owner) == tie.Type.Enemy:
                return 2
        return 1

    def get_best_path(self, start, goal):
        if goal not in self.tiles:
            return []

        unit = self.get_unit_on(start, False)
        if not unit:
            return []

        def heuristic(a, b):
            return a.distance(b)

        def get_cost(a):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a):
            return self.get_free_neighbours(unit, a)

        # if the unit can fit in at least 1 direction, go!
        for direction in Hex.directions:
            if self.unit_can_fit(unit, goal, Hex(qrs=direction)):
                return pathfinding.get_best_path(start, goal, heuristic, get_neighbours, get_cost)
        return []

    def get_reachable(self, unit):
        def get_cost(a):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a):
            return self.get_free_neighbours(unit, a)

        return pathfinding.get_reachable(unit.hex_coords, unit.move, get_neighbours, get_cost)
