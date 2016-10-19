from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty

from ui.hex_widget import HexWidget

from game import game_instance
from actions import ActionType
from core.hex_lib import Layout


class UnitActionTile(ButtonBehavior, HexWidget):
    action = StringProperty()
    key = StringProperty()

    def __init__(self, index, action_type, text, rk_skill=None, **kwargs):
        self.index = index
        self.action_type = action_type
        self.rk_skill = rk_skill
        self.action = text
        self.key = '[b]{0}[/b]'.format(index)
        super(UnitActionTile, self).__init__(**kwargs)


class ActionsBar(RelativeLayout):
    __Layouts__ = [[(0, -1)],
                   [(-1, 0), (0, -1)],
                   [(-1, 0), (0, 0), (0, -1)],
                   [(-1, 1), (0, 0), (-1, 0), (0, -1)],
                   [(-1, 1), (0, 0), (-1, 0), (0, -1), (-1, -1)],
                   [(-2, 1), (-1, 1), (0, 0), (-2, 0), (-1, 0), (0, -1)],
                   [(-2, 1), (-1, 1), (0, 0), (-2, 0), (-1, 0), (0, -1), (-1, -1)]]

    def __init__(self, **kwargs):
        super(ActionsBar, self).__init__(**kwargs)
        self.hex_layout = Layout(origin=self.pos, size=40, flat=True, margin=1)
        self.last_hovered_child = None

    def create(self):
        game_instance.current_fight.on_next_turn += lambda unit: self.on_new_action(unit, None, unit.actions_tree)
        game_instance.current_fight.on_action_change += self.on_new_action

    def create_action_widget(self, q, r, index, action_type, text, rk_skill=None):
        new_widget = UnitActionTile(index, action_type, text, rk_skill, q=q, r=r, layout=self.hex_layout)
        self.add_widget(new_widget)

    def on_new_action(self, unit, action_type, action_node, _rk_skill=None):
        self.clear_widgets()
        widget_data = []
        index = 1
        for a in action_node:
            if a.data in [ActionType.Weapon, ActionType.Skill]:
                for rk_skill in unit.get_skills(a.data):
                    widget_data.append((index, a.data, rk_skill.skill.name, rk_skill))
                    index += 1
            elif a.data != ActionType.EndTurn:
                widget_data.append((index, a.data, a.data.name, None))
                index += 1
        count = len(widget_data)  # not including the mandatory End Turn!
        assert(count < len(ActionsBar.__Layouts__))
        for i, (index, action_type, text, rk_skill) in enumerate(widget_data):
            q, r = ActionsBar.__Layouts__[count][i]
            self.create_action_widget(q, r, index, action_type, text, rk_skill)
        q, r = ActionsBar.__Layouts__[count][count]
        self.create_action_widget(q, r, 0, ActionType.EndTurn, 'End Turn')

    def _on_action_selected(self, index=None, button=None):
        if not button:
            for child in self.children:
                if child.index == index:
                    button = child
                    break
        if button:
            game_instance.current_fight.notify_action_change(button.action_type, button.rk_skill)

    def on_key_pressed(self, code, key):
        self._on_action_selected(index=int(key))

    def on_touch_down(self, touch):
        local_pos = self.to_local(*touch.pos)
        hover_hex = self.hex_layout.pixel_to_hex(local_pos)
        for child in self.children:
            if child.hex_coords == hover_hex:
                self._on_action_selected(button=child)
                return True
        return super(ActionsBar, self).on_touch_down(touch)

    def on_mouse_pos(self, stuff, pos):
        local_pos = self.to_local(*pos)
        hover_hex = self.hex_layout.pixel_to_hex(local_pos)
        for child in self.children:
            if child.hex_coords == hover_hex:
                if self.last_hovered_child != child:
                    if self.last_hovered_child:
                        self.last_hovered_child.selector.a = 0
                    child.selector.a = 1
                    self.last_hovered_child = child
                return True

        self.on_no_mouse_pos()
        return False

    def on_no_mouse_pos(self):
        if self.last_hovered_child:
            self.last_hovered_child.selector.a = 0
            self.last_hovered_child = None
