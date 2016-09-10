from enum import Enum
from utils.tree import Tree, Node


class ActionType(Enum):
    EndTurn = 0
    Move = 1
    Rotate = 2
    Weapon = 3
    Skill = 4


def to_string(action):
    txt = 'Action not Found!'
    if action == ActionType.EndTurn:
        txt = 'End Turn (0)'
    elif action == ActionType.Move:
        txt = 'Move (1)'
    elif action == ActionType.Rotate:
        txt = 'Rotate (2)'
    elif action == ActionType.Weapon:
        txt = 'Weapon (3)'
    elif action == ActionType.Skill:
        txt = 'Skill (4)'
    return txt


actions_trees = {
    # debug action tree
    'dbg': Tree(Node(ActionType.Move,
                     Node(ActionType.Rotate,
                          Node(ActionType.EndTurn)),
                     Node(ActionType.EndTurn)),
                Node(ActionType.Rotate,
                     Node(ActionType.EndTurn)),
                Node(ActionType.EndTurn)),
    # base action tree for most units
    'base': Tree(Node(ActionType.Move,
                      Node(ActionType.Weapon,
                           Node(ActionType.EndTurn)),
                      Node(ActionType.Skill,
                           Node(ActionType.EndTurn)),
                      Node(ActionType.Rotate,
                           Node(ActionType.EndTurn)),
                      Node(ActionType.EndTurn)),
                 Node(ActionType.Weapon,
                      Node(ActionType.EndTurn)),
                 Node(ActionType.Skill,
                      Node(ActionType.EndTurn)),
                 Node(ActionType.Rotate,
                      Node(ActionType.EndTurn)),
                 Node(ActionType.EndTurn))
}
