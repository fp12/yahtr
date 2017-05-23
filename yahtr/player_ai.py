from player import Player
from actions import ActionType
from utils.log import create_system_logger
from tie import TieType


logger = create_system_logger('AI')


class PlayerAI(Player):
    ai_controlled = True

    def __init__(self, *args):
        super(PlayerAI, self).__init__(*args)
        self.ennemies = []

    def __repr__(self):
        return f'AI<{self.name}>'

    def _refresh_ennemies(self):
        self.ennemies = [u for __, units in self.game.battle.squads.items() for u in units if self.game.battle.get_tie(self, u.owner) == TieType.enemy]

    def _get_closest_ennemy(self, current_unit):
        closest_nmi = self.ennemies[0]
        min_dist = current_unit.hex_coords.distance(closest_nmi.hex_coords)
        for u in self.ennemies[1:]:
            cur_dist = current_unit.hex_coords.distance(u.hex_coords)
            if cur_dist < min_dist:
                min_dist = cur_dist
                closest_nmi = u
        return closest_nmi, min_dist

    def start_turn(self, current_unit, actions_tree):
        # first, let's find the closest ennemy
        self._refresh_ennemies()
        closest_nmi, min_dist = self._get_closest_ennemy(current_unit)

        # now, can we hit it directly, or should we move?
        can_move = False
        best_action_score = 0
        best_ranked_skill = ()  # (action type, ranked skill)
        for a in actions_tree:
            if a.data in [ActionType.weapon, ActionType.skill]:
                for rk_skill in current_unit.get_skills(a.data):
                    for hun in rk_skill.skill.huns:
                        for hit in hun.H:
                            if hit.is_damage:
                                hit_length = hit.direction.destination.length
                                # can it hit directly?
                                if hit_length == min_dist:
                                    damage = rk_skill.hit_value(hit)
                                    logger.info(f'found hit: {rk_skill} - {damage} - {best_action_score}')
                                    if damage > best_action_score:
                                        best_action_score = damage
                                        best_ranked_skill = (a.data, rk_skill)
                                        # turn the unit so that it can use this skill
                                        current_unit.sim_move(orientation=current_unit.hex_coords.direction_to_distant(closest_nmi.hex_coords))
            elif a.data == ActionType.move:
                can_move = True

        if best_ranked_skill:
            logger.info(f'chosen {best_ranked_skill}')
            action_type, rk_skill = best_ranked_skill
            self.game.battle.notify_action_end(action_type, rk_skill=rk_skill)
        elif can_move:
            trajectory = self.game.battle.board.get_close_to(current_unit, closest_nmi)
            if len(trajectory) > 1 or trajectory[0] != current_unit.hex_coords:
                logger.info(f'we need to move {trajectory}')
                self.game.battle.notify_action_end(ActionType.move, trajectory=trajectory)
            else:
                logger.info('we can\'t even move')
                self.game.battle.notify_action_end(ActionType.end_turn)
        else:
            logger.info('nothing we can do yet, end this turn')
            self.game.battle.notify_action_end(ActionType.end_turn)
