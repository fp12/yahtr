from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from game import game_instance
import actions


class UnitActionButton(Button):
    def __init__(self, action_type, **kwargs):
        self.action_type = action_type
        super(UnitActionButton, self).__init__(**kwargs)


class ActionsBar(BoxLayout):
    def __init__(self, **kwargs):
        super(ActionsBar, self).__init__(orientation='horizontal', **kwargs)

    def create(self):
        game_instance.current_fight.on_next_turn += self.on_next
        game_instance.current_fight.on_action_change += self.on_new_action

    def on_next(self, unit, default_action_type):
        self.clear_widgets()
        # _, _, unit = game_instance.current_fight.time_bar.current
        available_actions = actions.actions_trees['dbg']  # unit.actions
        for a in available_actions:
            new_widget = UnitActionButton(action_type=a.data, text=actions.to_string(a.data))
            new_widget.bind(on_press=self.on_button_pressed)
            self.add_widget(new_widget)

    def on_new_action(self, action_type, action_node):
        self.clear_widgets()
        for a in action_node:
            new_widget = UnitActionButton(action_type=a.data, text=actions.to_string(a.data))
            new_widget.bind(on_press=self.on_button_pressed)
            self.add_widget(new_widget)

    def _on_action_selected(self, action_type):
        game_instance.current_fight.notify_action_change(action_type)

    def on_key_pressed(self, key):
        self._on_action_selected(actions.ActionType(int(key)))

    def on_button_pressed(self, button):
        self._on_action_selected(button.action_type)
