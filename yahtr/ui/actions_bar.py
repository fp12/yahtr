from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ObjectProperty

from ui.hex_widget import HexWidget

from game import game_instance
from actions import ActionType
from core.hex_lib import Layout
from utils import Color


class UnitActionTile(ButtonBehavior, HexWidget):
    action_key = ObjectProperty(None)
    action_name = ObjectProperty(None)

    colors = {
        ActionType.move: Color.action_move_rotate,
        ActionType.rotate: Color.action_move_rotate,
        ActionType.weapon: Color.action_weapon,
        ActionType.skill: Color.action_skill,
        ActionType.end_turn: Color.action_endturn
    }

    def __init__(self, index, action_type, text, rk_skill=None, **kwargs):
        super(UnitActionTile, self).__init__(color=self.colors[action_type], **kwargs)
        self.action_type = action_type
        self.rk_skill = rk_skill
        self.action_name.text = text
        self.action_index = index
        self.unselect()

    def select(self):
        self.action_key.text = ''
        self.action_name.color = [1, 1, 1, 1]

    def unselect(self):
        self.action_key.text = f'[b]{self.action_index}[/b]'
        self.action_name.color = [0.5, 0.5, 0.5, 1]


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
        self.selected_button = None

    def create(self):
        # game_instance.battle.on_new_turn += lambda unit: self.on_new_action(unit, None, unit.actions_tree)
        game_instance.battle.on_new_actions += self.on_new_actions

    def create_action_widget(self, q, r, index, action_type, text, rk_skill=None):
        new_widget = UnitActionTile(index, action_type, text, rk_skill, q=q, r=r, layout=self.hex_layout)
        self.add_widget(new_widget)

    def on_new_actions(self, unit, action_node):
        self.clear_widgets()
        if unit.ai_controlled:
            return

        widget_data = []
        index = 1
        for a in action_node:
            if a.data in [ActionType.weapon, ActionType.skill]:
                for rk_skill in unit.get_skills(a.data):
                    widget_data.append((index, a.data, _(rk_skill.skill.name), rk_skill))
                    index += 1
            elif a.data != ActionType.end_turn:
                widget_data.append((index, a.data, str(a.data), None))
                index += 1

        count = len(widget_data)  # not including the mandatory End Turn!
        assert count < len(ActionsBar.__Layouts__)

        for i, (index, action_type, text, rk_skill) in enumerate(widget_data):
            q, r = ActionsBar.__Layouts__[count][i]
            self.create_action_widget(q, r, index, action_type, text, rk_skill)
        q, r = ActionsBar.__Layouts__[count][count]
        self.create_action_widget(q, r, 0, ActionType.end_turn, str(ActionType.end_turn))

        self.selected_button = self.children[-1]
        self.selected_button.select()

    def _on_action_selected(self, index=None, button=None):
        if not button:
            for child in self.children:
                if child.action_index == index:
                    button = child
                    break

        if button and button != self.selected_button:
            self.selected_button.unselect()

            if button.action_type == ActionType.end_turn:
                game_instance.battle.notify_action_end(ActionType.end_turn)
            else:
                self.selected_button = button
                self.selected_button.select()
                game_instance.battle.notify_action_change(button.action_type, button.rk_skill)

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

    def on_mouse_pos(self, __, pos):
        local_pos = self.to_local(*pos)
        hover_hex = self.hex_layout.pixel_to_hex(local_pos)
        for child in self.children:
            if child.hex_coords == hover_hex:
                if self.last_hovered_child != child:
                    if self.last_hovered_child:
                        self.last_hovered_child.selector.hide()
                    child.selector.show()
                    self.last_hovered_child = child
                return True

        self.on_no_mouse_pos()
        return False

    def on_no_mouse_pos(self):
        if self.last_hovered_child:
            self.last_hovered_child.selector.hide()
            self.last_hovered_child = None
