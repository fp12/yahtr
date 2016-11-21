from player import Player
from skill import Effect
from actions import ActionType
from utils.log import log_main
import tie


logger = log_main.getChild('AI')


class PlayerAI(Player):
    def __init__(self, *args):
        super(PlayerAI, self).__init__(*args)
        self.ennemies = []

    def __repr__(self):
        return 'AI<{}>'.format(self.name)

    @property
    def ai_controlled(self):
        return True

    def _refresh_ennemies(self):
        self.ennemies = [u for _, units in self.game.battle.squads.items() for u in units if self.game.battle.get_tie(self, u.owner) == tie.Type.Enemy]

    def _get_closest_ennemy(self, current_unit):
        closest_nmi = self.ennemies[0]
        min_dist = current_unit.hex_coords.distance(closest_nmi.hex_coords)
        for u in self.ennemies[1:]:
            if current_unit.hex_coords.distance(u.hex_coords) < min_dist:
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
            if a.data in [ActionType.Weapon, ActionType.Skill]:
                for rk_skill in current_unit.get_skills(a.data):
                    for hun in rk_skill.skill.huns:
                        for hit in hun.H:
                            if Effect.damage in hit.effects:
                                # can it hit directly?
                                if hit.direction.destination.length == min_dist:
                                    damage = rk_skill.get_skill_health_change(hit)
                                    if damage < best_action_score:  # damage is <0
                                        best_action_score = damage
                                        best_ranked_skill = (a.data, rk_skill)
                                        # turn the unit so that it can use this skill
                                        current_unit.sim_move(orientation=current_unit.hex_coords.direction_to_distant(closest_nmi.hex_coords))
            elif a.data == ActionType.Move:
                can_move = True

        if best_ranked_skill:
            logger.info('chosen {}'.format(best_ranked_skill))
            action_type, rk_skill = best_ranked_skill
            self.game.battle.notify_action_end(action_type, rk_skill=rk_skill)
        elif can_move:
            trajectory = self.game.battle.board.get_close_to(current_unit, closest_nmi)
            if len(trajectory) > 1 or trajectory[0] != current_unit.hex_coords:
                logger.info('we need to move {}'.format(trajectory))
                self.game.battle.notify_action_end(ActionType.Move, trajectory=trajectory)
            else:
                logger.info('we can\'t even move')
                self.game.battle.notify_action_end(ActionType.EndTurn)
        else:
            logger.info('nothing we can do yet, end this turn')
            self.game.battle.notify_action_end(ActionType.EndTurn)
