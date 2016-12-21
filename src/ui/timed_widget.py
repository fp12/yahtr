from math import sqrt

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior

from ui.hex_widget import HexWidget

from game import game_instance
from core.hex_lib import Layout


class TimedWidget(ButtonBehavior, HexWidget):
    unit = ObjectProperty(None)
    selector = ObjectProperty(None)
    squad_color = ListProperty([1, 1, 1, 1])

    Radius = 40

    def set_unit(self, unit):
        self.unit = unit
        self.color = unit.color
        self.squad_color = unit.owner.color.color


class UnitInfoWidget(TimedWidget):
    Radius = TimedWidget.Radius * 3


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
        game_instance.battle.on_new_turn += self.on_next

    def on_next(self, unit):
        __, __, current_unit = game_instance.battle.time_bar.current
        self.info_widget.set_unit(current_unit)

        # killing them now, but may be animated later
        for child in self.children[:]:
            if child != self.info_widget:
                self.remove_widget(child)
        simulation = game_instance.battle.time_bar.simulate_for(len(TimedWidgetBar.Coords) + 1)
        for index, (priority, __, unit) in enumerate(simulation):
            if index > 0:
                q, r = TimedWidgetBar.Coords[index - 1]
                new_widget = TimedWidget(q=q, r=r, layout=self.hex_layout)
                new_widget.set_unit(unit)
                self.add_widget(new_widget)

    def get_unit_on_pos(self, pos):
        local_pos = self.to_local(*pos)
        local_hex = self.hex_layout.pixel_to_hex(local_pos)
        unit_on_pos = None
        for child in self.children:
            if child.hex_coords == local_hex:
                unit_on_pos = child.unit
                break
        else:
            local_hex = self.info_layout.pixel_to_hex(local_pos)
            if local_hex == (0, 0):
                unit_on_pos = self.info_widget.unit
        return unit_on_pos

    def on_mouse_pos(self, __, pos):
        hovered_unit = self.get_unit_on_pos(pos)
        if hovered_unit:
            if hovered_unit != self.last_hovered_unit:
                for child in self.children:
                    if child.unit == hovered_unit:
                        child.selector.show()
                    else:
                        child.selector.hide()
                self.last_hovered_unit = hovered_unit
            return True
        return False

    def on_no_mouse_pos(self):
        pass

    def on_touch_down(self, touch):
        clicked_unit = self.get_unit_on_pos(touch.pos)
        if clicked_unit:
            return True
