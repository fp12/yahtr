from copy import copy

from game_map import Map
from time_bar import TimeBar
import actions
from utils.event import Event
import tie


class Fight():
    def __init__(self, fight_map, players):
        self.current_map = Map(self, fight_map)
        self.squads = {p: [] for p in players}
        self.ties = []
        self.time_bar = TimeBar()
        self.started = False
        self.actions_history = []  # (unit, [ actions ])
        self.on_action_change = Event('unit', 'action_type', 'action_node', 'hit')
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
        rk_skills = unit.get_skills(unit.actions_tree.default.data)
        rk_skill = rk_skills[0] if rk_skills else None
        self.on_action_change(unit, unit.actions_tree.default.data, unit.actions_tree, rk_skill)

    def end_turn(self):
        # here check if all units are dead in one major squad
        self.time_bar.next()
        self.start_turn()

    def resolve_skill(self, unit, rk_skill):
        for hun_index, hun in enumerate(rk_skill.skill.huns):
            for hit_index, hit in enumerate(hun.H):
                hit_direction = copy(hit.direction.destination).rotate_to(unit.orientation)
                hitted_tile = hit_direction + unit.hex_coords
                hitted_unit = self.current_map.get_unit_on(hitted_tile)
                if hitted_unit:
                    damage = rk_skill.get_damage(hit)
                    if damage != 0:
                        hitted_unit.health_change(-damage, unit, hit)
            # here goes the hit pause

    def notify_action_change(self, action_type, rk_skill):
        if action_type == actions.ActionType.EndTurn:
            self.end_turn()
        else:
            unit, history = self.actions_history[-1]
            action_node = unit.actions_tree
            if history:
                action_node = unit.actions_tree.get_node_from_history(history)
            self.on_action_change(unit, action_type, action_node, rk_skill)

    def notify_action_end(self, action_type, rk_skill=None):
        unit, history = self.actions_history[-1]
        history.append(action_type)
        if rk_skill:
            self.resolve_skill(unit, rk_skill)
        new_action = unit.actions_tree.get_node_from_history(history)
        if new_action.default.data == actions.ActionType.EndTurn:
            self.end_turn()
        else:
            rk_skills = unit.get_skills(new_action.default.data)
            rk_skill = rk_skills[0] if rk_skills else None
            self.on_action_change(unit, new_action.default.data, new_action, rk_skill)

    def set_tie(self, p1, p2, tie_type):
        for t in self.ties:
            if t.has(p1, p2):
                t.tie_type = tie_type
                return
        self.ties.append(tie.Tie(p1, p2, tie_type))

    def get_tie(self, p1, p2):
        if p1 == p2:
            return tie.Type.Ally
        for t in self.ties:
            if t.has(p1, p2):
                return t.tie_type
        return tie.Type.Neutral
