from game_map import Map
from time_bar import TimeBar
import actions
from utils.event import Event


class Fight():
    def __init__(self, fight_map, players):
        self.current_map = Map(fight_map)
        self.squads = {p: [] for p in players}
        self.time_bar = TimeBar()
        self.started = False
        self.actions_history = []  # (unit, [ actions ])
        self.on_action_change = Event('action_type', 'action_node')
        self.on_next_turn = Event('unit')

    def deploy(self, squads):
        for squad_owner, units in squads.items():
            for player in self.squads.keys():
                if player == squad_owner:
                    self.squads[player] = units
                    self.current_map.register_units(units)
                    self.time_bar.register_units(units)

    def start(self):
        self.start_turn()
        self.started = True

    def start_turn(self):
        _, _, unit = self.time_bar.current
        self.actions_history.append((unit, []))
        self.on_next_turn(unit)
        self.on_action_change(unit.actions_tree.default.data, unit.actions_tree)

    def notify_action_change(self, action_type):
        if action_type == actions.ActionType.EndTurn:
            self.time_bar.next()
            self.start_turn()
        else:
            unit, history = self.actions_history[-1]
            action_node = unit.actions_tree
            if history:
                action_node = unit.actions_tree.get_node_from_history(history)
            self.on_action_change(action_type, action_node)

    def notify_action_end(self, action_type):
        unit, history = self.actions_history[-1]
        history.append(action_type)
        new_action = unit.actions_tree.get_node_from_history(history)
        if new_action.default.data == actions.ActionType.EndTurn:
            self.time_bar.next()
            self.start_turn()
        else:
            self.on_action_change(new_action.default.data, new_action)
