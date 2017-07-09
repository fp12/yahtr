from enum import Enum
from typing import NamedTuple

from yahtr.game import game_instance
from yahtr.ui.tile import Tile
from yahtr.utils.color import Color
from yahtr.utils.log import create_ui_logger


logger = create_ui_logger('ReachablePool')


class ReachableType(Enum):
    selected_unit = Color(98, 51, 142, 255)
    ally_unit = Color(86, 168, 79, 255)
    ennemy_unit = Color(191, 3, 3, 255)


class ReachablePool:
    """ All requests for reachable tiles go through this pool """

    class ReachableOwnerInfo(NamedTuple):
        """ utility class for info storage """
        owner: None  # Unit
        reachable_type: ReachableType

    _base_capacity = 50
    _margin = 2
    _c_invisible = Color(0, 0, 0, 0)

    def __init__(self):
        self.pool = []  # (tile, [ReachableOwnerInfo])
        self.units = []  # Unit
        self.hex_layout = None
        self.parent = None

    def setup(self, hex_layout, parent):
        self.parent = parent
        self.hex_layout = hex_layout
        for index in range(self._base_capacity):
            tile = self.create_tile(q=0, r=0)
            self.pool.append((tile, []))
            parent.add_widget(tile)

    def create_tile(self, q, r):
        return Tile(q=q, r=r,
                    layout=self.hex_layout,
                    color=self._c_invisible,
                    radius=self.hex_layout.radius - self._margin,
                    size=(self.hex_layout.radius - self._margin, self.hex_layout.radius - self._margin))

    def request_reachables(self, unit, r_type: ReachableType):
        if unit in self.units:
            logger.debug(f'Request cancelled - unit already present')
            return unit.reachables

        logger.debug(f'BEFORE request: {len(self.pool)} tiles in pool')

        # we get the reachable and we sort them as we sort the pool
        reachable_hexes = unit.reachables or sorted(game_instance.battle.board.get_reachable(unit), key=lambda h: (h.q, h.r))
        logger.debug(f'{len(reachable_hexes)} to process')

        pool_index = 0
        for h in reachable_hexes:
            while pool_index < len(self.pool):
                tile, owners = self.pool[pool_index]

                if len(owners) == 0:
                    # past this point, tiles are only dangling
                    self.assign(pool_index, h, unit, r_type)
                    pool_index += 1
                    break

                q, r = tile.hex_coords.q, tile.hex_coords.r
                if q == h.q and r == h.r:
                    # in this case, the tile is already at the the good place and we may just need to activate it
                    self.assign(pool_index, h, unit, r_type)
                    pool_index += 1
                    break
                elif q > h.q or (q == h.q and r > h.r):
                    # in this case, the tile doesn't exist, we'll take it from the available tiles or create one
                    self.move_available_tile_to(pool_index)
                    self.assign(pool_index, h, unit, r_type)
                    pool_index += 1
                    break
                else:
                    pool_index += 1
            else:
                self.move_available_tile_to(pool_index)
                self.assign(pool_index, h, unit, r_type)
                pool_index += 1

        logger.debug(f'AFTER request: {len(self.pool)} tiles in pool')
        self.units.append(unit)
        return reachable_hexes

    def release_reachables(self, unit):
        if unit not in self.units:
            # legit case for inits, cleanups...
            return

        pool_index = 0
        pool_capacity = len(self.pool)  # won't change during this function
        while pool_index < pool_capacity:
            tile, owners = self.pool[pool_index]

            if len(owners) == 0:
                # past this point, tiles are only dangling
                break

            for owner_info in owners:
                if owner_info.owner == unit:
                    owners.remove(owner_info)
                    if len(owners) == 0:
                        # we first hide it
                        tile.color = self._c_invisible
                        self.pool[pool_index] = (tile, owners)
                        # we move this tile to the end as it is not relevant anymore
                        self.pool.insert(pool_capacity, self.pool.pop(pool_index))
                    else:
                        tile.color = Color.merge(set(o.reachable_type.value for o in owners))
                        self.pool[pool_index] = (tile, owners)
                        pool_index += 1
                    break
            else:
                pool_index += 1
        self.units.remove(unit)

    def move_available_tile_to(self, tile_index):
        if tile_index >= len(self.pool):
            tile = self.create_tile(q=0, r=0)
            self.pool.append((tile, []))
            self.parent.add_widget(tile)
        else:
            for index in range(tile_index + 1, len(self.pool)):
                tile, owners = self.pool[index]
                if len(owners) == 0:
                    self.pool.insert(tile_index, self.pool.pop(index))
                    break
            else:
                tile = self.create_tile(q=0, r=0)
                self.pool.insert(tile_index, (tile, []))
                self.parent.add_widget(tile)

    def assign(self, tile_index, hex_coords, unit, r_type):
        tile, owners = self.pool[tile_index]
        for owner_info in owners:
            if owner_info.owner == unit:
                logger.error('Unit is already present')
                return
        owners.append(self.ReachableOwnerInfo(unit, r_type))
        tile.move_to(hex_coords)
        tile.color = Color.merge(set(o.reachable_type.value for o in owners))
        self.pool[tile_index] = (tile, owners)


reachable_pool = ReachablePool()
