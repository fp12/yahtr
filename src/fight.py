import threading
from copy import copy

from game_map import Map
from time_bar import TimeBar
import actions
from utils.event import Event, UniqueEvent
import tie


class SkillContext:
    def __init__(self, unit):
        self.unit = unit
        self.base_unit_coords = copy(unit.hex_coords)
        self.base_unit_orientation = copy(unit.orientation)
        self.previous_target_angle = None  # used for choosing the rotation direction


class Fight:
    def __init__(self, fight_map, players):
        self.current_map = Map(self, fight_map)
        self.squads = {p: [] for p in players}
        self.ties = []
        self.time_bar = TimeBar()
        self.started = False
        self.actions_history = []  # (unit, [ actions ])
        self.thread_event = ()  # (threading.Event, callback)

        # events
        self.on_action_change = Event('unit', 'action_type', 'action_node', 'hit')
        self.on_next_turn = Event('unit')
        self.on_skill_turn = UniqueEvent()

    def update(self, *args):
        if self.thread_event:
            evt, cb = self.thread_event
            if evt.is_set():
                cb()
                self.thread_event = ()

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
        if unit.owner.ai_controlled:
            unit.owner.start_turn(unit)

    def end_turn(self):
        # here check if all units are dead in one major squad
        self.time_bar.next()
        self.start_turn()

    def _end_action_end(self, unit, history):
        new_action = unit.actions_tree.get_node_from_history(history)
        if new_action.default.data == actions.ActionType.EndTurn:
            self.end_turn()
        else:
            rk_skills = unit.get_skills(new_action.default.data)
            rk_skill = rk_skills[0] if rk_skills else None
            self.on_action_change(unit, new_action.default.data, new_action, rk_skill)

    def resolve_skill(self, unit, rk_skill):
        """ Note: NOT executed on main thread """
        def get_move_context(context, unit, move_info):
            epsilon = 0.000001
            context.move_info = move_info
            context.end_coords = copy(unit.hex_coords)
            if move_info.move:
                move_direction = move_info.move.destination - move_info.move.origin
                coords_offset = move_direction.rotate_to(context.base_unit_orientation)
                context.end_coords += coords_offset

            context.end_orientation = copy(context.base_unit_orientation)
            context.target_angle = 0
            if move_info.orientation:
                context.end_orientation = copy(move_info.orientation.destination).rotate_to(context.base_unit_orientation)
                base_angle = context.base_unit_coords.angle_to_neighbour(context.base_unit_orientation)
                context.target_angle = base_angle + move_info.orientation.angle
                if move_info.orientation.angle == -180 and context.previous_target_angle:
                    if context.target_angle > context.previous_target_angle:
                        context.previous_target_angle = context.target_angle
                        context.target_angle -= epsilon
                    else:
                        context.previous_target_angle = context.target_angle
                        context.target_angle += epsilon
                else:
                    context.previous_target_angle = context.target_angle

        context = SkillContext(unit)

        for hun in rk_skill.skill.huns:
            for hit in hun.H:
                health_change = rk_skill.get_skill_health_change(hit)

                base_direction = hit.direction.destination - hit.direction.origin
                context.direction = base_direction.rotate_to(context.base_unit_orientation)
                hitted_tile = context.base_unit_coords + copy(hit.direction.destination).rotate_to(context.base_unit_orientation)
                origin_tile = hitted_tile - context.direction
                hitted_wall = self.current_map.get_wall_between(hitted_tile, origin_tile)
                if hitted_wall:
                    if health_change < 0:
                        self.current_map.wall_damage(hitted_wall, health_change)
                else:
                    hitted_unit = self.current_map.get_unit_on(hitted_tile)
                    if hitted_unit and health_change != 0:
                        if health_change < 0:
                            shield_index = hitted_unit.get_shield(origin_tile, hitted_tile)
                            if shield_index != -1:
                                hitted_unit.shield_change(shield_index, context)
                            else:
                                context.hit = hit
                                hitted_unit.health_change(health_change, context)
                        else:
                            context.hit = hit
                            hitted_unit.health_change(health_change, context)

            if hun.U:
                get_move_context(context, unit, hun.U)
                unit.skill_move(context)

            for move_info in hun.N:
                move_origin_offset = copy(move_info.move.origin).rotate_to(context.base_unit_orientation)
                move_origin = context.base_unit_coords + move_origin_offset
                moved_unit = self.current_map.get_unit_on(move_origin)
                if moved_unit:
                    get_move_context(context, moved_unit, move_info)
                    moved_unit.skill_move(context)

            ui_thread_event = self.on_skill_turn()
            if ui_thread_event:
                ui_thread_event.wait()

        self.thread_event[0].set()

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

        self.thread_event = (threading.Event(), lambda: self._end_action_end(unit, history))
        if rk_skill:
            skill_thread = threading.Thread(target=self.resolve_skill, args=(unit, rk_skill))
            skill_thread.start()
        else:
            self.thread_event[0].set()

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
