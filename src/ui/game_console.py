from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect

from utils.log import game_console_handler


class GameConsole(ScrollView):
    messages = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameConsole, self).__init__(effect_cls=ScrollEffect, **kwargs)
        game_console_handler.on_message += self.on_message_received

    def on_message_received(self, message):
        def f(dt=None):
            self.messages.text = '\n'.join([self.messages.text, message]) if self.messages.text else message
            self.scroll_y = 0
        Clock.schedule_once(f)

    def on_mouse_pos(self, *args):
        local_pos = self.to_local(*args[1])
        return self.collide_point(*local_pos)
