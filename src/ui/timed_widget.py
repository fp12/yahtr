from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from game import game_instance


class TimedWidget(Button):
    pass


class TimedWidgetBar(BoxLayout):
    def __init__(self, max_widgets, **kwargs):
        super(TimedWidgetBar, self).__init__(orientation='vertical', **kwargs)
        self.max_widgets = max_widgets

    def create(self):
        game_instance.current_fight.on_next_turn += self.on_next

    def on_next(self, unit, default_action_type):
        self.clear_widgets()
        simulation = game_instance.current_fight.time_bar.simulate_for(self.max_widgets)
        for priority, _, unit in simulation:
            text = '{0} ({1})'.format(unit.template_name, priority)
            new_widget = TimedWidget(text=text, color=[0, 0, 0, 1], background_normal='', background_color=unit.color + [1])
            self.add_widget(new_widget)
