from heapq import heappush, heappop, heapify


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, element, priority):
        heappush(self.elements, [priority, element])

    def get(self):
        if len(self.elements) > 0:
            return heappop(self.elements)[1]
        else:
            return None

    def get_with_priority(self):
        if len(self.elements) > 0:
            return heappop(self.elements)
        else:
            return None


class EqualPriorityQueue(PriorityQueue):
    def put(self, element, priority=0):
        for existing_element in self.elements:
            # this priority already exists: we update the existing element with the new
            if existing_element[0] == priority:
                existing_element[1].append(element)
                heapify(self.elements)
                return

        new_elem = (priority, [element])
        heappush(self.elements, new_elem)
