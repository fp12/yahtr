#cython: language_level=3


cdef class Hex:
    cdef readonly int q, r
    cdef list neighbours

    cpdef int distance(self, Hex other)

    cpdef Hex get_neighbour(self, size_t direction)
    cpdef list get_neighbours(self)

    cpdef int angle_to_neighbour(self, Hex neighbour)

    cpdef Hex rotate_to(self, Hex direction)

    cpdef Hex direction_to_distant(self, Hex other)

    @staticmethod
    cdef Hex get_round(double fq, double fr)