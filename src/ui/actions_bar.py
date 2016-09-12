from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from game import game_instance
from actions import ActionType


class UnitActionButton(Button):
    def __init__(self, index, action_type, skill=None, **kwargs):
        self.index = index
        self.action_type = action_type
        self.skill = skill
        super(UnitActionButton, self).__init__(**kwargs)


class ActionsBar(BoxLayout):
    def create(self):
        game_instance.current_fight.on_next_turn += lambda unit: self.on_new_action(unit, None, unit.actions_tree)
        game_instance.current_fight.on_action_change += self.on_new_action

    def create_action_widget(self, index, action_type, text, skill=None):
        new_widget = UnitActionButton(index=index, action_type=action_type, text=text, skill=skill)
        new_widget.bind(on_press=self.on_button_pressed)
        self.add_widget(new_widget)

    def on_new_action(self, unit, action_type, action_node, skill=None):
        self.clear_widgets()
        index = 1
        for a in action_node:
            if a.data in [ActionType.Weapon, ActionType.Skill]:
                for skill in unit.get_skills(a.data):
                    self.create_action_widget(index=index, action_type=a.data, text=skill.name, skill=skill)
                    index += 1

            elif a.data == ActionType.EndTurn:
                self.create_action_widget(index=0, action_type=a.data, text='End Turn')

            else:
                self.create_action_widget(index=index, action_type=a.data, text=a.data.name)
                index += 1

    def _on_action_selected(self, index, button=None):
        if not button:
            for ch in self.children:
                if ch.index == index:
                    button = ch
                    break
        if button:
            game_instance.current_fight.notify_action_change(button.action_type, button.skill)

    def on_key_pressed(self, code, key):
        self._on_action_selected(int(key))

    def on_button_pressed(self, button):
        self._on_action_selected(button.index)
