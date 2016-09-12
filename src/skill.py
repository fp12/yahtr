import data_loader
from hex_lib import Hex


class HexDir:
    def __init__(self, data):
        q0, r0, q1, r1 = data
        self.origin = Hex(q=q0, r=r0)
        self.destination = Hex(q=q1, r=r1)
        self.angle = self.origin.angle_to_neighbour(self.destination - self.origin)

    def __repr__(self):
        return 'From {0} To {1}'.format(self.origin, self.destination)


class HUN:
    def __init__(self, hun):
        self.hits = []
        self.unit_move = None
        self.ennemy_moves = []
        if 'H' in hun:
            for h_def in hun['H']:
                self.hits.append(HexDir(h_def))
        if 'U' in hun:
            self.unit_move = HexDir(hun['U'])
        if 'N' in hun:
            for n_def in hun['N']:
                self.ennemy_moves.append(HexDir(h_def))

    @property
    def H(self):
        return self.hits

    @property
    def U(self):
        return self.unit_move

    @property
    def N(self):
        return self.ennemy_moves

    def __repr__(self):
        return 'Hits: {0}\n\tUnit move: {1}\n\tNMIs moves: {2}'.format(self.hits, self.unit_move, self.ennemy_moves)


class Skill:
    def __init__(self, name, data):
        self.name = name
        self.huns = []
        if 'HUN' in data:
            for hun in data['HUN']:
                self.huns.append(HUN(hun))

    def __repr__(self):
        return 'Sk<{0}>\n\t{1}'.format(self.name, '\n\t'.join(map(repr, self.huns)))


class RankedSkill:
    def __init__(self, skill, rank):
        self.skill = skill
        self.rank = rank


def load_all(root_path):
    raw_skills = data_loader.local_load(root_path + 'data/skills/', '.json')
    return [Skill(name, data) for name, data in raw_skills.items()]