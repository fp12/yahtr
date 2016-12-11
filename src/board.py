from enum import Enum
from math import floor
from copy import copy

import data_loader
from core.hex_lib import Hex, get_hex_direction
from core import pathfinding
from wall import Wall, WallType
from utils.event import Event
from utils import attr

import tie


class BoardType(Enum):
    Custom = 0
    Parallelogram = 1
    Triangle = 2
    Hexagon = 3
    Rectangle = 4


class Board():
    default_move_cost = 1
    close_to_ennemy_move_cost = 2

    def __init__(self, battle, name):
        self.battle = battle
        self.name = name

        data = data_loader.local_load_single('data/boards/', name, '.json')
        self.holes = data['holes'] if 'holes' in data else None
        self.tiles = [Hex(*qr) for qr in data['adds']] if 'adds' in data else []
        self.walls = [Wall(d) for d in data['walls']] if 'walls' in data else []

        if data['type'] == BoardType.Parallelogram.name:
            attr.get_from_dict(self, data['info'], 'q1', 'q2', 'r1', 'r2')
            self._get_tiles_parallelogram()
        elif data['type'] == BoardType.Triangle.name:
            attr.get_from_dict(self, data['info'], 'size')
            self._get_tiles_triangle()
        elif data['type'] == BoardType.Hexagon.name:
            attr.get_from_dict(self, data['info'], 'radius')
            self._get_tiles_hexagon()
        elif data['type'] == BoardType.Rectangle.name:
            attr.get_from_dict(self, data['info'], 'height', 'width')
            self._get_tiles_rectangle()

        self.units = []  # ref

        self.on_wall_hit = Event('origin', 'destination', 'destroyed')
        self.on_unit_removed = Event('unit')

    def register_units(self, units):
        self.units.extend(units)

    def unregister_unit(self, unit):
        self.on_unit_removed(unit)
        self.units.remove(unit)

    def _validate_not_hole(self, q, r):
        if self.holes and [q, r] in self.holes:
            return False
        return True

    def get_wall_between(self, origin, destination):
        return next((w for w in self.walls if w == (origin, destination)), None)

    def wall_damage(self, wall, damage):
        if WallType.breakable in wall.types:
            self.on_wall_hit(wall.origin, wall.destination, destroyed=True)
            self.walls.remove(wall)
        else:
            self.on_wall_hit(wall.origin, wall.destination, destroyed=False)

    def get_tiles(self):
        return self.tiles

    def _get_tiles_parallelogram(self):
        for q in range(self.q1, self.q2 + 1):
            for r in range(self.r1, self.r2 + 1):
                if self._validate_not_hole(q, r):
                    self.tiles.append(Hex(q, r))

    def _get_tiles_triangle(self):
        for q in range(self.size + 1):
            for r in range(self.size - q, self.size + 1):
                if self._validate_not_hole(q, r):
                    self.tiles.append(Hex(q, r))

    def _get_tiles_hexagon(self):
        for q in range(-self.radius, self.radius + 1):
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            for r in range(r1, r2 + 1):
                if self._validate_not_hole(q, r):
                    self.tiles.append(Hex(q, r))

    def _get_tiles_rectangle(self):
        for r in range(self.height):
            r_offset = floor(r / 2.)
            for q in range(-r_offset, self.width - r_offset):
                if self._validate_not_hole(q, r):
                    self.tiles.append(Hex(q, r))

    def get_unit_on(self, hex_coords, include_shape=True):
        for u in self.units:
            if u.hex_coords == hex_coords:
                return u
            if include_shape and u.hex_test(hex_coords):
                return u
        return None

    def get_free_neighbours(self, unit, hex_coords):
        units_hexes = []
        for u in self.units:
            if u != unit:
                units_hexes.extend(u.current_shape)

        for neighbour in hex_coords.get_neighbours():
            if self.get_wall_between(hex_coords, neighbour):
                continue
            orientation = neighbour - hex_coords
            for shape_part in unit.calc_shape_at(neighbour, orientation):
                if shape_part not in self.tiles or shape_part in units_hexes:
                    break
            else:
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
            if other_unit and self.battle.get_tie(unit.owner, other_unit.owner) == tie.Type.Enemy:
                return Board.close_to_ennemy_move_cost
        return Board.default_move_cost

    def get_best_path(self, unit, goal):
        if goal not in self.tiles:
            return []

        def heuristic(a, b):
            return a.distance(b)

        def get_cost(a):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a):
            return self.get_free_neighbours(unit, a)

        # if the unit can fit in at least 1 direction, go!
        for i in range(6):
            if self.unit_can_fit(unit, goal, get_hex_direction(i)):
                return pathfinding.Path(unit.hex_coords, unit.move, heuristic, get_neighbours, get_cost).get_best_to_goal(goal)
        return []

    def get_close_to(self, unit, target):
        target_shape = copy(target.current_shape)

        def heuristic(a, b):
            return a.distance(b)

        def get_cost(a):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a):
            return self.get_free_neighbours(unit, a)

        return pathfinding.Path(unit.hex_coords, unit.move, heuristic, get_neighbours, get_cost).get_best_to_shape(target_shape)

    def get_reachable(self, unit):
        def get_cost(a):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a):
            return self.get_free_neighbours(unit, a)

        return pathfinding.Reachable(unit.hex_coords, unit.move, get_neighbours, get_cost).get()
