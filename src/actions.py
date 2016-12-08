from enum import Enum

import data_loader
from utils.tree import Tree, Node
from localization.ids import *


class ActionType(Enum):
    EndTurn = 0
    Move = 1
    Rotate = 2
    Weapon = 3
    Skill = 4

    def get_loc(self):
        if self.value == ActionType.Move.value:
            return L_Move
        if self.value == ActionType.Rotate.value:
            return L_Rotate
        if self.value == ActionType.EndTurn.value:
            return L_EndTurn


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


def load_all(root_path):
    raw_data = data_loader.local_load(root_path + 'data/actions_trees/', '.txt')
    return [ActionTree(file, data) for file, data in raw_data.items()]
