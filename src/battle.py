import threading
from copy import copy

from board import Board
from time_bar import TimeBar
from actions import ActionType
import tie
from utils.event import Event, UniqueEvent
from utils.log import log_game


log_battle = log_game.getChild('battle')


class SkillContext:
    def __init__(self, unit):
        self.unit = unit
        self.base_unit_coords = copy(unit.hex_coords)
        self.base_unit_orientation = copy(unit.orientation)
        self.previous_target_angle = None  # used for choosing the rotation direction


class Battle:
    def __init__(self, battle_board, players):
        self.board = Board(self, battle_board)
        self.squads = {p: [] for p in players}
        self.ties = []
        self.time_bar = TimeBar()
        self.actions_history = []  # (unit, [ actions ])
        self.thread_event = ()  # (threading.Event, callback)

        # events
        self.on_action_change = Event('unit', 'action_type', 'action_node', 'hit')
        self.on_new_turn = Event('unit')
        self.on_action = UniqueEvent()

    def update(self, *args):
        if self.thread_event:
            evt, cb = self.thread_event
            if evt.is_set():
                self.thread_event = ()
                cb()

    def deploy(self, squads):
        for squad_owner, units in squads.items():
            for player in self.squads.keys():
                if player == squad_owner:
                    self.squads[player] = units
                    self.board.register_units(units)
                    self.time_bar.register_units(units)

    def start(self):
        log_battle.info('Battle started')
        self.start_turn()

    def start_turn(self):
        _, _, unit = self.time_bar.current
        log_battle.info('New turn started [{}]'.format(unit))
        self.actions_history.append((unit, []))
        self.on_new_turn(unit)
        rk_skills = unit.get_skills(unit.actions_tree.default.data)
        rk_skill = rk_skills[0] if rk_skills else None
        self.on_action_change(unit, unit.actions_tree.default.data, unit.actions_tree, rk_skill)
        if unit.ai_controlled:
            unit.owner.start_turn(unit, unit.actions_tree)

    def end_turn(self):
        # here check if all units are dead in one major squad
        self.time_bar.next()
        self.start_turn()

    def _end_action_end(self, unit, history):
        new_action = unit.actions_tree.get_node_from_history(history)
        if new_action.default.data == ActionType.EndTurn:
            self.end_turn()
        else:
            rk_skills = unit.get_skills(new_action.default.data)
            rk_skill = rk_skills[0] if rk_skills else None
            self.on_action_change(unit, new_action.default.data, new_action, rk_skill)
            if unit.ai_controlled:
                unit.owner.start_turn(unit, new_action)

    def resolve_move(self, unit, context):
        trajectory = context.get('trajectory')
        assert trajectory

        unit.sim_move(trajectory)

        ui_thread_event = self.on_action()
        if ui_thread_event:
            ui_thread_event.wait()

        self.thread_event[0].set()

    def resolve_skill(self, unit, context):
        rk_skill = context.get('rk_skill')
        assert rk_skill

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
                hitted_wall = self.board.get_wall_between(hitted_tile, origin_tile)
                if hitted_wall:
                    if health_change < 0:
                        self.board.wall_damage(hitted_wall, health_change)
                else:
                    hitted_unit = self.board.get_unit_on(hitted_tile)
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
                moved_unit = self.board.get_unit_on(move_origin)
                if moved_unit:
                    get_move_context(context, moved_unit, move_info)
                    moved_unit.skill_move(context)

            ui_thread_event = self.on_action()
            if ui_thread_event:
                ui_thread_event.wait()

        self.thread_event[0].set()

    def notify_action_change(self, action_type, rk_skill=None):
        unit, history = self.actions_history[-1]
        action_node = unit.actions_tree
        if history:
            action_node = unit.actions_tree.get_node_from_history(history)
        self.on_action_change(unit, action_type, action_node, rk_skill)

    def notify_action_end(self, action_type, **kwargs):
        unit, history = self.actions_history[-1]
        history.append(action_type)
        log_battle.info('Action: {} {}'.format(action_type.name, kwargs or ''))

        if action_type == ActionType.EndTurn:
            self.end_turn()
            return

        if action_type == ActionType.Move:
            action_resolution_function = self.resolve_move
        elif action_type in [ActionType.Weapon, ActionType.Skill]:
            action_resolution_function = self.resolve_skill
        else:
            log_battle.error('Unsupported action_type')
            action_resolution_function = None

        assert not self.thread_event, '{}'.format(self.thread_event)
        self.thread_event = (threading.Event(), lambda: self._end_action_end(unit, history))
        action_thread = threading.Thread(target=action_resolution_function, args=(unit, kwargs))
        action_thread.start()

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
