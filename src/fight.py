from game_map import Map
from time_bar import TimeBar
import actions


class Fight():
    def __init__(self, fight_map, players):
        self.current_map = Map(fight_map)
        self.squads = {p: [] for p in players}
        self.time_bar = TimeBar()
        self.started = False
        self.actions_history = []  # (unit, [ actions ])
        self.callbacks = {'on_action_change': [], 'on_next_turn': []}

    def deploy(self, squads):
        for squad_owner, units in squads.items():
            for player in self.squads.keys():
                if player == squad_owner:
                    self.squads[player] = units
                    self.current_map.register_units(units)
                    self.time_bar.register_units(units)

    def register_event(self, on_action_change=None, on_next_turn=None):
        if on_action_change:
            self.callbacks['on_action_change'].append(on_action_change)
        if on_next_turn:
            self.callbacks['on_next_turn'].append(on_next_turn)

    def start(self):
        self.start_turn()
        self.started = True

    def start_turn(self):
        _, _, unit = self.time_bar.current
        self.actions_history.append((unit, []))
        self.call_on_next_turn(unit, None)
        self.call_on_action_change(actions.actions_trees['dbg'].default.data, actions.actions_trees['dbg'])

    def notify_action_change(self, action_type):
        if action_type == actions.ActionType.EndTurn:
            self.time_bar.next()
            self.start_turn()
        else:
            unit, history = self.actions_history[-1]
            action_node = actions.actions_trees['dbg']
            if history:
                action_node = actions.actions_trees['dbg'].get_node_from_history(history)
            self.call_on_action_change(action_type, action_node)

    def notify_action_end(self, action_type):
        _, _, unit = self.time_bar.current
        aunit, history = self.actions_history[-1]
        assert(aunit == unit)
        history.append(action_type)
        new_action = actions.actions_trees['dbg'].get_node_from_history(history)
        print(new_action.default)
        if new_action.default.data == actions.ActionType.EndTurn:
            self.time_bar.next()
            self.start_turn()
        else:
            self.call_on_action_change(new_action.default.data, new_action)

    def call_on_action_change(self, action_type, action_node):
        for cb in self.callbacks['on_action_change']:
            cb(action_type, action_node)

    def call_on_next_turn(self, unit, default_action_type):
        for cb in self.callbacks['on_next_turn']:
            cb(unit, default_action_type)
