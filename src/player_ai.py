from player import Player
from skill import Effect
from actions import ActionType
import tie


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
        self.ennemies = [u for _, units in self.game.current_fight.squads.items() for u in units if self.game.current_fight.get_tie(self, u.owner) == tie.Type.Enemy]

    def _get_closest_ennemy(self, current_unit):
        closest_nmi = self.ennemies[0]
        min_dist = current_unit.hex_coords.distance(closest_nmi.hex_coords)
        for u in self.ennemies[1:]:
            if current_unit.hex_coords.distance(u.hex_coords) < min_dist:
                closest_nmi = u
        return closest_nmi, min_dist

    def start_turn(self, current_unit):
        # first, let's find the closest ennemy
        self._refresh_ennemies()
        closest_nmi, min_dist = self._get_closest_ennemy(current_unit)

        # now, can we hit it directly, or should we move?
        can_move = False
        best_action_score = 0
        best_ranked_skill = ()  # (action type, ranked skill)
        for a in current_unit.actions_tree:
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
            print('chosen', best_ranked_skill)
            self.game.current_fight.notify_action_end(*best_ranked_skill)
        elif can_move:
            trajectory = self.game.current_fight.current_map.get_close_to(current_unit, closest_nmi)
            print('we need to move', trajectory)
            current_unit.sim_move(trajectory)
        else:
            print('nothing we can do yet, end this turn')
            self.game.current_fight.notify_action_change(ActionType.EndTurn, None)
