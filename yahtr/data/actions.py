from yahtr.data.core import DataTemplate
from yahtr.utils.tree import Tree, Node
from yahtr.localization.enum import LocalizedEnum


class ActionType(LocalizedEnum):
    end_turn = 0
    move = 1
    rotate = 2
    weapon = 3
    skill = 4
    undo_move = 5


class ActionsTree(DataTemplate):
    __path = 'data/actions_trees/'
    __ext = '.txt'

    __separator = '  '
    __comment_token = '#'

    def __init__(self, file_id, data, **kwargs):
        super(ActionsTree, self).__init__(file_id, **kwargs)
        self.tree = Tree()
        self.__load_tree(data)

    def __load_tree(self, data):
        current_tabs_count = -1
        cursor = [self.tree]
        for line in data:
            if line.startswith(self.__comment_token):
                continue
            tabs_count = line.count(self.__separator)
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

    @staticmethod
    def load_all(**kwargs):
        raw_data = DataTemplate.local_load(ActionsTree.__path, ActionsTree.__ext)
        return [ActionsTree(file, data, **kwargs) for file, data in raw_data.items()]

    @staticmethod
    def load_one(actions_tree_id, **kwargs):
        data = DataTemplate.local_load_single(ActionsTree.__path, actions_tree_id, ActionsTree.__ext)
        if data:
            return ActionsTree(actions_tree_id, data, **kwargs)
        return None
