from yahtr.data_loader import local_load, local_load_single
from yahtr.utils.tree import Tree, Node
from yahtr.localization.enum import LocalizedEnum


class ActionType(LocalizedEnum):
    end_turn = 0
    move = 1
    rotate = 2
    weapon = 3
    skill = 4
    undo_move = 5


class ActionTree:
    separator = '  '
    comment_token = '#'

    def __init__(self, file, data):
        self.id = file
        self.tree = Tree()
        self.__load_tree(data)

    def __load_tree(self, data):
        current_tabs_count = -1
        cursor = [self.tree]
        for line in data:
            if line.startswith(self.comment_token):
                continue
            tabs_count = line.count(self.separator)
            action_type = ActionType[line.strip()]
            current_node = Node(action_type)
            if tabs_count > current_tabs_count:
                cursor[-1].add_node(current_node)
            elif tabs_count == current_tabs_count:
                cursor.pop(-1)
                cursor[-1].add_node(current_node)
            else:  # tabs_count < current_tabs_count
                diff = current_tabs_count - tabs_count + 1
                for __ in range(diff):
                    cursor.pop(-1)
                cursor[-1].add_node(current_node)
            cursor.append(current_node)
            current_tabs_count = tabs_count


__path = 'data/actions_trees/'
__ext = '.txt'


def load_all_actions_trees():
    raw_data = local_load(__path, __ext)
    return [ActionTree(file, data) for file, data in raw_data.items()]


def load_one_actions_tree(actions_tree_id):
    data = local_load_single(__path, actions_tree_id, __ext)
    if data:
        return ActionTree(actions_tree_id, data)
    return None
