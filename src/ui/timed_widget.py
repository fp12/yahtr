from math import sqrt

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior

from ui.hex_widget import HexWidget

from game import game_instance
from hex_lib import Layout


class TimedWidget(ButtonBehavior, HexWidget):
    UnitText = StringProperty()
    unit = ObjectProperty(None)
    selector = ObjectProperty(None)

    Radius = 40

    def __init__(self, unit, prio, **kwargs):
        super(TimedWidget, self).__init__(**kwargs)
        self.unit = unit
        self.color = unit.color + [1]
        self.UnitText = '{0}\n({1})'.format(self.unit.template.name, prio)


class UnitInfoWidget(ButtonBehavior, HexWidget):
    unit = ObjectProperty(None)
    selector = ObjectProperty(None)

    Radius = TimedWidget.Radius * 3

    def set_unit(self, unit):
        self.unit = unit
        self.color = unit.color + [1]


class TimedWidgetBar(RelativeLayout):
    Coords = [(0, 0), (1, 0), (1, 1), (0, 2), (0, 3), (1, 3), (1, 4), (0, 5), (0, 6), (1, 6)]

    def __init__(self, **kwargs):
        super(TimedWidgetBar, self).__init__(**kwargs)
        self.margin = 1
        self.hex_layout = Layout(origin=self.pos, size=TimedWidget.Radius, flat=True, margin=self.margin)

        info_pos_x = self.x - UnitInfoWidget.Radius - TimedWidget.Radius / 2 - self.margin
        info_pos_y = self.y - sqrt(3) / 2 * TimedWidget.Radius
        self.info_layout = Layout(origin=(info_pos_x, info_pos_y), size=UnitInfoWidget.Radius, flat=True, margin=self.margin)
        self.info_widget = UnitInfoWidget(q=0, r=0, layout=self.info_layout)
        self.add_widget(self.info_widget)

        self.last_hovered_unit = None

    def get_pos_for_actions_bar(self):
        return (self.info_layout.origin.x - self.margin, self.y)

    def create(self):
        game_instance.current_fight.on_next_turn += self.on_next

    def on_next(self, unit):
        _, _, current_unit = game_instance.current_fight.time_bar.current
        self.info_widget.set_unit(current_unit)

        # killing them now, but may be animated later
        for child in self.children[:]:
            if child != self.info_widget:
                self.remove_widget(child)
        simulation = game_instance.current_fight.time_bar.simulate_for(len(TimedWidgetBar.Coords) + 1)
        for index, (priority, _, unit) in enumerate(simulation):
            if index > 0:
                q, r = TimedWidgetBar.Coords[index - 1]
                new_widget = TimedWidget(unit, priority, q=q, r=r, layout=self.hex_layout)
                self.add_widget(new_widget)

    def get_unit_on_pos(self, pos):
        local_pos = self.to_local(*pos)
        local_hex = self.hex_layout.pixel_to_hex(local_pos).get_round()
        unit_on_pos = None
        for child in self.children:
            if child.hex_coords == local_hex:
                unit_on_pos = child.unit
                break
        else: # no break
            local_hex = self.info_layout.pixel_to_hex(local_pos).get_round()
            if local_hex == (0, 0):
                unit_on_pos = self.info_widget.unit
        return unit_on_pos

    def on_mouse_pos(self, stuff, pos):
        hovered_unit = self.get_unit_on_pos(pos)
        if hovered_unit != self.last_hovered_unit:
            for child in self.children:
                if child.unit == hovered_unit:
                    child.selector.a = 1
                else:
                    child.selector.a = 0
            self.last_hovered_unit = hovered_unit
            return True
        return False

    def on_touch_down(self, touch):
        clicked_unit = self.get_unit_on_pos(touch.pos)
        if clicked_unit:
            return True
