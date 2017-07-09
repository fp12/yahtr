import threading
from copy import copy

from yahtr.tie import Tie, TieType
from yahtr.board import Board
from yahtr.data.bank import data_bank
from yahtr.data.skill_template import Target
from yahtr.time_bar import TimeBar
from yahtr.data.actions import ActionType
from yahtr.utils.event import Event, UniqueEvent
from yahtr.utils.log import create_game_logger
from yahtr.localization.ids import L_LOG_BATTLE_STARTED, L_LOG_NEW_TURN, L_LOG_ACTION


logger = create_game_logger('battle')


class SkillContext:
    def __init__(self, unit):
        self.unit = unit
        self.base_unit_coords = copy(unit.hex_coords)
        self.base_unit_orientation = copy(unit.orientation)
        self.previous_target_angle = None  # used for choosing the rotation direction
        self.targets = []  # (target, type)
        self.targets_killed = []  # (target, type) will be set later by unit


class Battle:
    def __init__(self, board_id, players):
        self.board = Board(data_bank.get_board_template(board_id), self)
        self.time_bar = TimeBar()
        self.squads = {p: [] for p in players}
        self.ties = []
        self.actions_history = []  # (unit, [ actions ])
        self.thread_event = ()  # (threading.Event, callback)
        self.targets = []  # list of (target, {args})

        # events
        self.on_new_turn = Event('unit')
        self.on_new_actions = Event('unit', 'action_node')
        self.on_select_action = Event('unit', 'action_type', 'rk_skill')
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
        logger.info(L_LOG_BATTLE_STARTED)
        self.start_turn()

    def _load_new_actions(self, unit, start_action):
        self.on_new_actions(unit, start_action)
        if unit.ai_controlled:
            unit.owner.start_turn(unit, start_action)

    def clean_all_reachables(self):
        for __, units in self.squads.items():
            for u in units:
                u.reachables = []

    def start_turn(self):
        __, __, unit = self.time_bar.current
        logger.info(L_LOG_NEW_TURN.format(unit))
        self.actions_history.append((unit, []))

        # cleanup cached data
        self.clean_all_reachables()

        self.on_new_turn(unit)
        self._load_new_actions(unit, unit.actions_tree)

    def end_turn(self):
        # here check if all units are dead in one major squad
        self.time_bar.next()
        self.start_turn()

    def _end_action_end(self, unit, history):
        new_action = unit.actions_tree.get_node_from_history(history)
        if not new_action.has_leaves():
            self.end_turn()
        else:
            self._load_new_actions(unit, new_action)

    def resolve_rotate(self, unit, context):
        """ Note: NOT executed on main thread """
        self.thread_event[0].set()

    def resolve_move(self, unit, context):
        """ Note: NOT executed on main thread """
        trajectory = context.get('trajectory')
        assert trajectory

        unit.sim_move(trajectory)

        ui_thread_event = self.on_action()
        if ui_thread_event:
            ui_thread_event.wait()

        self.thread_event[0].set()

    def resolve_undo_move(self, unit, context):
        """ Note: NOT executed on main thread """
        unit.sim_move([unit.hex_coords, unit.prev_hex_coords])

        ui_thread_event = self.on_action()
        if ui_thread_event:
            ui_thread_event.wait()

        history_unit, history = self.actions_history[-1]
        assert unit is history_unit
        assert len(history) >= 2

        del history[-1]  # remove the undo_move action
        del history[-1]  # remove the move action

        self.thread_event[0].set()

    @staticmethod
    def get_move_context(context: SkillContext, unit, move_info):
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

    def resolve_skill(self, unit, context):
        """ Note: NOT executed on main thread """
        rk_skill = context.get('rk_skill')
        assert rk_skill

        ctx = SkillContext(unit)

        for hun in rk_skill.skill.huns:
            for hit in hun.H:
                hit_value = rk_skill.hit_value(hit)
                if hit_value == 0:
                    continue

                base_direction = hit.direction.destination - hit.direction.origin
                ctx.direction = base_direction.rotate_to(ctx.base_unit_orientation)
                hitted_tile = ctx.base_unit_coords + copy(hit.direction.destination).rotate_to(ctx.base_unit_orientation)
                origin_tile = hitted_tile - ctx.direction
                if hit.valid_on_target(Target.wall):
                    hitted_wall = self.board.get_wall_between(hitted_tile, origin_tile)
                    if hitted_wall:
                        ctx.targets.append((hitted_wall, Target.wall))
                        self.board.wall_damage(hitted_wall, -hit_value)
                        continue

                hitted_unit = self.board.get_unit_on(hitted_tile)
                if not hitted_unit:
                    continue

                ctx.hit = hit
                if hit.is_damage and hit.valid_on_target(Target.shield):
                    shield_index = hitted_unit.get_shield(origin_tile, hitted_tile)
                    if shield_index != -1:
                        ctx.targets.append((hitted_unit, Target.shield))
                        hitted_unit.shield_change(shield_index, ctx)
                        continue

                ctx.targets.append((hitted_unit, Target.unit))
                hitted_unit.health_change(hit_value * (-1 if hit.is_damage else 1), ctx)

            if hun.U:
                self.get_move_context(ctx, unit, hun.U)
                unit.skill_move(ctx)

            for move_info in hun.N:
                move_origin_offset = copy(move_info.move.origin).rotate_to(ctx.base_unit_orientation)
                move_origin = ctx.base_unit_coords + move_origin_offset
                moved_unit = self.board.get_unit_on(move_origin)
                if moved_unit:
                    self.get_move_context(ctx, moved_unit, move_info)
                    moved_unit.skill_move(ctx)

            ui_thread_event = self.on_action()
            if ui_thread_event:
                ui_thread_event.wait()

                # here we do the cleanup if some units / walls are killed
                for target, target_type in ctx.targets_killed:
                    if target_type == Target.unit:
                        self.board.unregister_unit(target)
                        self.time_bar.unregister_unit(target)
                        self.squads[target.owner].remove(target)

        self.thread_event[0].set()

    def pre_resolve_skill(self, action_type, rk_skill):
        unit, history = self.actions_history[-1]

        ctx = SkillContext(unit)

        for hun in rk_skill.skill.huns:
            for hit in hun.H:
                hit_value = rk_skill.hit_value(hit)
                if hit_value == 0:
                    continue

                base_direction = hit.direction.destination - hit.direction.origin
                ctx.direction = base_direction.rotate_to(ctx.base_unit_orientation)
                hitted_tile = ctx.base_unit_coords + copy(hit.direction.destination).rotate_to(ctx.base_unit_orientation)
                origin_tile = hitted_tile - ctx.direction
                if hit.valid_on_target(Target.wall):
                    hitted_wall = self.board.get_wall_between(hitted_tile, origin_tile)
                    if hitted_wall:
                        ctx.targets.append((hitted_wall, Target.wall))
                        self.board.wall_targeted(hitted_wall)
                        self.targets.append((self.board, {'wall': hitted_wall}))
                        continue

                hitted_unit = self.board.get_unit_on(hitted_tile)
                if not hitted_unit:
                    continue

                ctx.hit = hit
                if hit.is_damage and hit.valid_on_target(Target.shield):
                    shield_index = hitted_unit.get_shield(origin_tile, hitted_tile)
                    if shield_index != -1:
                        ctx.targets.append((hitted_unit, Target.shield))
                        hitted_unit.shield_targeted(shield_index, ctx)
                        self.targets.append((hitted_unit, {'shield_index': shield_index}))
                        continue

                ctx.targets.append((hitted_unit, Target.unit))
                hitted_unit.unit_targeted(hit_value * (-1 if hit.is_damage else 1), ctx)
                self.targets.append((hitted_unit, {}))

            if hun.U:
                self.get_move_context(ctx, unit, hun.U)
                # TODO: UNIT MOVE

            for move_info in hun.N:
                move_origin_offset = copy(move_info.move.origin).rotate_to(ctx.base_unit_orientation)
                move_origin = ctx.base_unit_coords + move_origin_offset
                moved_unit = self.board.get_unit_on(move_origin)
                if moved_unit:
                    self.get_move_context(ctx, moved_unit, move_info)
                    # TODO: NMI MOVE

    def notify_action_change(self, action_type, rk_skill):
        self.clean_targets()

        unit, __ = self.actions_history[-1]
        self.on_select_action(unit, action_type, rk_skill)

    def notify_action_end(self, action_type, **kwargs):
        self.clean_targets()

        unit, history = self.actions_history[-1]
        history.append(action_type)
        logger.info(L_LOG_ACTION.format(action_type.name, kwargs or ''))

        if action_type == ActionType.end_turn:
            self.end_turn()
            return

        if action_type == ActionType.move:
            action_resolution_function = self.resolve_move
        elif action_type == ActionType.undo_move:
            action_resolution_function = self.resolve_undo_move
        elif action_type == ActionType.rotate:
            action_resolution_function = self.resolve_rotate
        elif action_type in [ActionType.weapon, ActionType.skill]:
            action_resolution_function = self.resolve_skill
        else:
            logger.error('Unsupported action_type')
            action_resolution_function = None

        assert not self.thread_event, f'{self.thread_event}'
        self.thread_event = (threading.Event(), lambda: self._end_action_end(unit, history))
        thread = threading.Thread(target=action_resolution_function, args=(unit, kwargs))
        thread.start()

    def notify_action_validation(self, action_type, rk_skill):
        self.clean_targets()

        # ActionType.move is validated by pathfinding
        # ActionType.rotate and undo_move don't need validation
        if action_type not in [ActionType.weapon, ActionType.skill]:
            return

        self.pre_resolve_skill(action_type, rk_skill)

    def clean_targets(self):
        if self.targets:
            for t, args in self.targets:
                t.end_targeting(**args)
            self.targets = []

    def set_tie(self, p1, p2, tie_type):
        for t in self.ties:
            if t.has(p1, p2):
                t.tie_type = tie_type
                return
        self.ties.append(Tie(p1, p2, tie_type))

    def get_tie(self, p1, p2):
        if p1 == p2:
            return TieType.ally
        for t in self.ties:
            if t.has(p1, p2):
                return t.tie_type
        return TieType.neutral

    def get_tie_with_selected_unit(self, other_unit):
        current_unit, __ = self.actions_history[-1]
        return self.get_tie(current_unit.owner, other_unit.owner)
