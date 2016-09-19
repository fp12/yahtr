from math import sqrt

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior

from ui.hex_widget import HexWidget

from game import game_instance
from hex_lib import Layout


class TimedWidget(ButtonBehavior, HexWidget):
    UnitText = StringProperty()
    Radius = 40

    def __init__(self, unit, prio, **kwargs):
        super(TimedWidget, self).__init__(**kwargs)
        self.unit = unit
        self.color = unit.color + [1]
        self.UnitText = '{0}\n({1})'.format(self.unit.template.name, prio)


class UnitInfoWidget(ButtonBehavior, HexWidget):
    Radius = TimedWidget.Radius * 3

    def __init__(self, **kwargs):
        super(UnitInfoWidget, self).__init__(**kwargs)
        self.unit = None

    def set_unit(self, unit):
        self.unit = unit
        self.color = unit.color + [1]

        self.clear_widgets()
        self.add_widget(Label(text='[b]{0}[/b]'.format(unit.template.name), center=self.pos, halign='center', markup=True))


class TimedWidgetBar(ScatterLayout):
    Coords = [(0,0), (1,0), (1,1), (0,2), (0,3), (1,3), (1,4), (0,5), (0,6), (1,6)]

    def __init__(self, **kwargs):
        super(TimedWidgetBar, self).__init__(**kwargs)
        self.margin = 1
        self.hex_layout = Layout(origin=self.pos, size=TimedWidget.Radius, flat=True, margin=self.margin)

        info_pos_x = self.x - UnitInfoWidget.Radius - TimedWidget.Radius / 2 - self.margin
        info_pos_y = self.y - sqrt(3) / 2 * TimedWidget.Radius
        self.info_layout = Layout(origin=(info_pos_x, info_pos_y), size=UnitInfoWidget.Radius, flat=True, margin=self.margin)

        self.info_widget = UnitInfoWidget(q=0, r=0, layout=self.info_layout)
        self.add_widget(self.info_widget)

    def get_pos_for_actions_bar(self):
        return (self.info_layout.origin.x - self.margin, self.y)

    def create(self):
        game_instance.current_fight.on_next_turn += self.on_next

    def on_next(self, unit):
        _, _, current_unit = game_instance.current_fight.time_bar.current
        self.info_widget.set_unit(current_unit)

        # killing them now, but may be animated later
        for child in self.content.children[:]:
            if child != self.info_widget:
                self.remove_widget(child)
        simulation = game_instance.current_fight.time_bar.simulate_for(len(TimedWidgetBar.Coords) + 1)
        for index, (priority, _, unit) in enumerate(simulation):
            if index > 0:
                q, r = TimedWidgetBar.Coords[index - 1]
                new_widget = TimedWidget(unit, priority, q=q, r=r, layout=self.hex_layout)
                self.add_widget(new_widget)
