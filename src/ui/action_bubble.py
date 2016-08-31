from kivy.properties import StringProperty

from ui.colored_widget import ColoredWidget
from ui.action_arrow import ActionArrow

from game import game_instance
from hex_lib import Hex


class ActionBubble(ColoredWidget):
    bubble_txt = StringProperty('')

    def __init__(self, text, action, unit, color=[0.5, 1, 0, 0.5], **kwargs):
        super(ActionBubble, self).__init__(color=color, size_hint=(None, None), **kwargs)
        self.bubble_txt = str(text)
        self._action = action
        self._action_arrows = []
        self._unit = unit

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clear()
            self.load_action()
            return True

    def clear(self):
        for x in self._action_arrows:
            self.parent.remove_widget(x)
        self._action_arrows = []

    def load_action(self):
        for h in game_instance.actions[self._action]['hits']:
            h_origin = self._unit.hex_coords + Hex(qrs=h['origin'])
            h_direction = self._unit.hex_coords + Hex(qrs=h['direction'])
            pos = self._unit.hex_layout.get_mid_edge_position(h_origin, h_direction)
            angle = h_origin.angle_to_neighbour(h_direction)
            arrow = ActionArrow(angle=angle, pos=(pos.x, pos.y))
            self._action_arrows.append(arrow)
            self.parent.add_widget(arrow)
