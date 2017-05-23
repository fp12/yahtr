import threading

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock

from ui.game_view import GameView
from ui.timed_widget import TimedWidgetBar
from ui.actions_bar import ActionsBar
from ui.game_console import GameConsole
from ui.anim_scheduler import AnimScheduler

from game_data import game_data
from game import game_instance


Builder.load_file('yahtr/ui/kv/main_window.kv')


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

        self.debug_print_keys = False

        self.layout = None
        self.game_view = None
        self.time_bar = None
        self.actions_bar = None
        self.game_console = None

        self._key_binder = {}
        self.anim_scheduler = AnimScheduler()

        Window.bind(on_key_down=self.on_keyboard_down, mouse_pos=self.on_mouse_pos)

    def on_start(self):
        # load static data
        game_data.load()

        # prepare UI
        self.game_console = GameConsole(pos=(10, 10), size_hint=(0.25, 0.25))
        self.layout.add_widget(self.game_console, 0)

        self.time_bar = TimedWidgetBar(y=75, pos_hint={'right': 0.95}, size_hint=(None, 1), width=75)
        self.layout.add_widget(self.time_bar, 1)

        self.actions_bar = ActionsBar(pos=self.time_bar.get_pos_for_actions_bar(), size_hint=(None, None))
        self.layout.add_widget(self.actions_bar, 2)

        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size, auto_bring_to_front=False)
        self.layout.add_widget(self.game_view, 3)

        # load dynamic setup
        game_instance.load_battle_setup('chess_demo')
        game_instance.battle.on_action += self.on_battle_action

        # link widgets through events
        self.game_view.on_unit_hovered += self.time_bar.on_unit_hovered_external
        self.time_bar.on_unit_hovered += self.game_view.on_unit_hovered_external

        self.game_view.load_board()
        self.game_view.load_squads()
        self.time_bar.create()
        self.actions_bar.create()

        self._key_binder.update({'q': [self.game_view.on_debug_key, self.on_debug_key],
                                 'shift+=': [self.game_view.on_zoom_down],
                                 '+': [self.game_view.on_zoom_down],
                                 '-': [self.game_view.on_zoom_up],
                                 'a': [self.game_view.on_move_key],
                                 's': [self.game_view.on_move_key],
                                 'd': [self.game_view.on_move_key],
                                 'w': [self.game_view.on_move_key],
                                 ' ': [self.game_view.on_center_key],
                                 'c': [self.print_children],
                                 '0': [self.actions_bar.on_key_pressed],
                                 '1': [self.actions_bar.on_key_pressed],
                                 '2': [self.actions_bar.on_key_pressed],
                                 '3': [self.actions_bar.on_key_pressed],
                                 '4': [self.actions_bar.on_key_pressed],
                                 '5': [self.actions_bar.on_key_pressed],
                                 '6': [self.actions_bar.on_key_pressed],
                                 '7': [self.actions_bar.on_key_pressed],
                                 '8': [self.actions_bar.on_key_pressed],
                                 '9': [self.actions_bar.on_key_pressed]
                                 })

        game_instance.battle.start()

        Clock.schedule_interval(game_instance.update, 1 / 30.)

    def on_battle_action(self):
        if self.anim_scheduler.ready_to_start():
            event = threading.Event()
            self.anim_scheduler.start(event)
            return event
        return None

    def build(self):
        self.layout = FloatLayout()
        self.title = 'Yet Another Hex Tactical RPG'
        return self.layout

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers):
        code = '{}+{}'.format('.'.join(modifiers), text) if modifiers else text
        if self.debug_print_keys:
            print('keycode:`{}` | code:`{}`'.format(keycode, code))
        if code in self._key_binder:
            for cb in self._key_binder[code]:
                cb(keycode, code)
            return True

    def on_debug_key(self, keycode, code):
        self.debug_print_keys = not self.debug_print_keys

    def on_mouse_pos(self, *args):
        """dispatching mouse position by priority order"""
        dispatch_success = False
        for child in self.layout.children[:]:
            if dispatch_success:
                child.on_no_mouse_pos()
            else:
                dispatch_success = child.on_mouse_pos(*args)

    def print_children(self, *args):
        def recurse(w, tab):
            for c in w.children:
                print('\t' * tab, c)
                recurse(c, tab + 1)
        recurse(self.layout, 0)
