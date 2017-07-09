from enum import Enum

from kivy.uix.relativelayout import RelativeLayout

from yahtr.utils.event import Event


class ReachableToggleType(Enum):
    selected = 0
    others = 1


class SelectedReachableMode(Enum):
    on = 0
    off = 1

    def next(self):
        return SelectedReachableMode.off if self is SelectedReachableMode.on else SelectedReachableMode.on


class OthersReachableMode(Enum):
    none = 0
    allies = 1
    ennemies = 2
    allies_and_ennemies = 3

    def next(self):
        if self is OthersReachableMode.none:
            return OthersReachableMode.allies
        if self is OthersReachableMode.allies:
            return OthersReachableMode.ennemies
        if self is OthersReachableMode.ennemies:
            return OthersReachableMode.allies_and_ennemies
        return OthersReachableMode.none


class GameOptions(RelativeLayout):
    def __init__(self, **kvargs):
        super(GameOptions, self).__init__(**kvargs)
        self.selected_reachable_mode = SelectedReachableMode.on
        self.others_reachable_mode = OthersReachableMode.none
        self.on_toggle_reachables = Event('what', 'new_mode')

    def on_toggle_player_reachables(self):
        self.selected_reachable_mode = self.selected_reachable_mode.next()
        self.on_toggle_reachables(ReachableToggleType.selected, self.selected_reachable_mode)

    def on_toggle_other_reachables(self):
        self.others_reachable_mode = self.others_reachable_mode.next()
        self.on_toggle_reachables(ReachableToggleType.others, self.others_reachable_mode)
