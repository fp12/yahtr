from enum import Enum
from utils.tree import Tree, Node


class ActionType(Enum):
    EndTurn = 0
    Move = 1
    Rotate = 2
    Weapon = 3
    Skill = 4


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
                 Node(ActionType.EndTurn)),
    # base action tree for rogues (can use weapons twice)
    'rogue': Tree(Node(ActionType.Move,
                       Node(ActionType.Weapon,
                            Node(ActionType.Weapon,
                                 Node(ActionType.EndTurn)),
                            Node(ActionType.EndTurn)),
                       Node(ActionType.Skill,
                            Node(ActionType.EndTurn)),
                       Node(ActionType.Rotate,
                            Node(ActionType.EndTurn)),
                       Node(ActionType.EndTurn)),
                  Node(ActionType.Weapon,
                       Node(ActionType.Weapon,
                            Node(ActionType.EndTurn)),
                       Node(ActionType.EndTurn)),
                  Node(ActionType.Skill,
                       Node(ActionType.EndTurn)),
                  Node(ActionType.Rotate,
                       Node(ActionType.EndTurn)),
                  Node(ActionType.EndTurn))
}
