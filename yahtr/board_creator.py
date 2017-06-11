from math import floor

from yahtr.core.hex_lib import Hex


def build_parallelogram(tiles, holes, q1, q2, r1, r2):
    for q in range(q1, q2 + 1):
        for r in range(r1, r2 + 1):
            if (q, r) not in holes:
                tiles.append(Hex(q, r))


def build_triangle(tiles, holes, size):
    for q in range(size + 1):
        for r in range(size - q, size + 1):
            if (q, r) not in holes:
                tiles.append(Hex(q, r))


def build_hexagon(tiles, holes, radius):
    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        for r in range(r1, r2 + 1):
            if (q, r) not in holes:
                tiles.append(Hex(q, r))


def build_rectangle(tiles, holes, height, width):
    for r in range(height):
        r_offset = floor(r / 2.)
        for q in range(-r_offset, width - r_offset):
            if (q, r) not in holes:
                tiles.append(Hex(q, r))
