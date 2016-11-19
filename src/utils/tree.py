class Tree:
    def __init__(self, *nodes):
        self.nodes = []
        for n in nodes:
            if isinstance(n, Node) and n not in self.nodes:
                self.nodes.append(n)

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
        return 'Tree:\n' + ''.join(n._display(1) for n in self.nodes)

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
        separator = '\t' * deep
        return str(self.data) + '\n' + ''.join(separator + n._display(deep + 1) for n in self.nodes)

    def __repr__(self):
        return self._display(1)
