from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from ui.colored_widget import ColoredWidget

from game import game_instance


class TimedWidget(Button):
    pass


class TimedWidgetBar(BoxLayout):
    def __init__(self, max_widgets, **kwargs):
        super(TimedWidgetBar, self).__init__(orientation='vertical', **kwargs)
        self.max_widgets = max_widgets
        self.widgets = []
        
    def create(self):
        simulation = game_instance.current_fight.time_bar.simulate_for(self.max_widgets)
        for priority, counter, unit in simulation:
            text = '{0} ({1})'.format(unit.template_name, priority)
            new_widget = TimedWidget(text=text, color=[0,0,0,1], background_normal='', background_color=unit.template['color']+[1])
            self.add_widget(new_widget)
            self.widgets.append(new_widget)
