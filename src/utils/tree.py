class Tree:
    def __init__(self, *nodes):
        self.nodes = []
        for node in nodes:
            if type(node) == Node and node not in self.nodes:
                self.nodes.append(node)

    def get_node_from_history(self, history):
        current_node = self
        for k in history:
            for n in current_node.nodes:
                if k == n.data:
                    current_node = n
                    break
            else:
                return None
        return current_node

    def __repr__(self):
        txt = 'Tree:\n'
        for n in self.nodes:
            txt += n._display(1)
        return txt

    def __iter__(self):
        return self.nodes.__iter__()

    @property
    def default(self):
        return self.nodes[0]


class Node(Tree):
    def __init__(self, data, *nodes):
        self.data = data
        super(Node, self).__init__(*nodes)

    def _display(self, deep):
        txt = str(self.data) + '\n'
        for n in self.nodes:
            txt += '\t' * deep + n._display(deep + 1)
        return txt

    def __repr__(self):
        return self._display(1)
