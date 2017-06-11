from enum import Enum
from copy import copy

from yahtr.data_loader import local_load, local_load_single
from yahtr.core.hex_lib import Hex, get_hex_direction
from yahtr.core import pathfinding
from yahtr.wall import Wall, WallType
from yahtr.utils.event import Event
from yahtr.utils import attr
from yahtr.tie import TieType
from yahtr.board_creator import build_parallelogram, build_triangle, build_hexagon, build_rectangle


class BoardType(Enum):
    custom = 0
    parallelogram = 1
    triangle = 2
    hexagon = 3
    rectangle = 4


class BoardTemplate:
    """ Board as defined in data """

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

        BoardTemplate.__creators[self.type](self.tiles, self.holes, **self.info)


class Board:
    """ Board as instantiated ingame """

    __attributes = ['holes', 'tiles', 'walls']

    default_move_cost = 1
    close_to_ennemy_move_cost = 2

    def __init__(self, template, battle):
        self.template = template
        attr.copy_from_instance(template, self, *Board.__attributes)
        self.battle = battle

        self.units = []  # ref

        self.on_wall_hit = Event('origin', 'destination', 'destroyed')
        self.on_unit_removed = Event('unit')

    def register_units(self, units: list):
        self.units.extend(units)

    def unregister_unit(self, unit):
        self.on_unit_removed(unit)
        self.units.remove(unit)

    def get_wall_between(self, origin, destination):
        return next((w for w in self.walls if w == (origin, destination)), None)

    def wall_damage(self, wall, damage):
        if WallType.breakable in wall.types:
            self.on_wall_hit(wall.origin, wall.destination, destroyed=True)
            self.walls.remove(wall)
        else:
            self.on_wall_hit(wall.origin, wall.destination, destroyed=False)

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
            if other_unit and self.battle.get_tie(unit.owner, other_unit.owner) == TieType.enemy:
                return Board.close_to_ennemy_move_cost
        return Board.default_move_cost

    def get_best_path(self, unit, goal: Hex):
        if goal not in self.tiles:
            return []

        def heuristic(a: Hex, b: Hex):
            return a.distance(b)

        def get_cost(a: Hex):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a: Hex):
            return self.get_free_neighbours(unit, a)

        # if the unit can fit in at least 1 direction, go!
        for i in range(6):
            if self.unit_can_fit(unit, goal, get_hex_direction(i)):
                return pathfinding.Path(unit.hex_coords, unit.move, heuristic, get_neighbours, get_cost).get_best_to_goal(goal)
        return []

    def get_close_to(self, unit, target):
        target_shape = copy(target.current_shape)

        def heuristic(a: Hex, b: Hex):
            return a.distance(b)

        def get_cost(a: Hex):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a: Hex):
            return self.get_free_neighbours(unit, a)

        return pathfinding.Path(unit.hex_coords, unit.move, heuristic, get_neighbours, get_cost).get_best_to_shape(target_shape)

    def get_reachable(self, unit):
        def get_cost(a: Hex):
            # could be cached later
            return self._get_cost(unit, a)

        def get_neighbours(a: Hex):
            return self.get_free_neighbours(unit, a)

        return pathfinding.Reachable(unit.hex_coords, unit.move, get_neighbours, get_cost).get()


__path = 'data/boards/'
__ext = '.json'


def load_all_board_templates():
    raw_data = local_load(__path, __ext)
    return [BoardTemplate(file, data) for file, data in raw_data.items()]


def load_one_board_template(board_id):
    data = local_load_single(__path, board_id, __ext)
    if data:
        return BoardTemplate(board_id, data)
    return None
