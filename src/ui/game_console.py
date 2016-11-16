from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from utils.log import game_console_handler


class GameConsole(Widget):
    messages = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameConsole, self).__init__(**kwargs)
        game_console_handler.on_message += self.on_message

    def on_message(self, message):
        def f(dt=None):
            print('displaying', message)
            self.messages.text = message
        Clock.schedule_once(f)
