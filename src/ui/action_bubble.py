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
            print('removing ', x)
            self.parent.remove_widget(x)
        self._action_arrows = []

    def load_action(self):
        for h in game_instance.actions[self._action]['hits']:
            h_origin = self._unit._hex + Hex(qrs=h['origin'])
            h_direction = self._unit._hex + Hex(qrs=h['direction'])
            pos = self._unit._layout.get_mid_edge_position(h_origin, h_direction)
            c1 = self._unit._layout.hex_to_pixel(h_origin)
            c2 = self._unit._layout.hex_to_pixel(h_direction)
            print('hex', self._unit._hex, self.pos)
            print('origin', h_origin, c1)
            print('direction', h_direction, c2)
            print((c1.x + (c2.x - c1.x) / 2, c1.y + (c2.y - c1.y) / 2))
            angle = h_origin.angle_to_neighbour(h_direction)
            arrow = ActionArrow(angle=angle, pos=(pos.x, pos.y))
            self._action_arrows.append(arrow)
            self.parent.add_widget(arrow)
