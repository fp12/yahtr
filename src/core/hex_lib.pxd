cdef class Hex:
    cdef int _q, _r

    cpdef distance(self, Hex other)

    cpdef get_neighbours(self)

    cpdef Hex get_neighbour(self, size_t direction)

    cpdef angle_to_neighbour(self, Hex neighbour)

    cpdef rotate_to(self, Hex direction)

    cpdef Hex direction_to_distant(self, Hex other)

    @staticmethod
    cdef Hex get_round(double fq, double fr)