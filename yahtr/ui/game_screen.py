import threading

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock

from yahtr.ui.game_view import GameView
from yahtr.ui.timed_widget import TimedWidgetBar
from yahtr.ui.actions_bar import ActionsBar
from yahtr.ui.game_console import GameConsole
from yahtr.ui.anim_scheduler import anim_scheduler

from yahtr.game import game_instance


Builder.load_file('yahtr/ui/kv/game_screen.kv')


class GameScreen(Screen):
    def __init__(self, battle_options, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.battle_options = battle_options

        self.debug_print_keys = False

        self.game_view = None
        self.time_bar = None
        self.actions_bar = None
        self.game_console = None

        self._key_binder = {}

        Window.bind(on_key_down=self.on_keyboard_down, mouse_pos=self.on_mouse_pos)

    def on_enter(self):
        # prepare UI
        self.game_console = GameConsole(pos=(10, 10), size_hint=(0.25, 0.25))
        self.add_widget(self.game_console, 0)

        self.time_bar = TimedWidgetBar(pos=(-10, 75), pos_hint={'right': 1}, size_hint=(None, None))
        self.add_widget(self.time_bar, 1)

        self.actions_bar = ActionsBar(pos=self.time_bar.get_pos_for_actions_bar(), pos_hint={'right': 1}, size_hint=(None, None))
        self.add_widget(self.actions_bar, 2)

        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size, auto_bring_to_front=False)
        self.add_widget(self.game_view, 3)

        # load dynamic setup
        game_instance.load_battle_setup(self.battle_options['setup_name'])
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

    def on_pre_leave(self):
        game_instance.battle.on_action -= self.on_battle_action
        self.game_view.on_unit_hovered -= self.time_bar.on_unit_hovered_external
        self.time_bar.on_unit_hovered -= self.game_view.on_unit_hovered_external

        for child in self.children[:]:
            self.remove_widget(child)

    def on_battle_action(self):
        if anim_scheduler.ready_to_start():
            event = threading.Event()
            anim_scheduler.start(event)
            return event
        return None

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers):
        code = '{}+{}'.format('.'.join(modifiers), text) if modifiers else text
        if self.debug_print_keys:
            print(f'keycode:`{keycode}` | code:`{code}`')
        if code in self._key_binder:
            for cb in self._key_binder[code]:
                cb(keycode, code)
            return True

    def on_debug_key(self, keycode, code):
        self.debug_print_keys = not self.debug_print_keys

    def on_mouse_pos(self, *args):
        """dispatching mouse position by priority order"""
        if not self.get_root_window():
            return False

        dispatch_success = False
        for child in self.children[:]:
            if dispatch_success:
                if getattr(child, 'on_no_mouse_pos', None):
                    child.on_no_mouse_pos()
            else:
                if getattr(child, 'on_mouse_pos', None):
                    dispatch_success = child.on_mouse_pos(*args)

    def print_children(self, *args):
        def recurse(w, tab):
            for c in w.children:
                print('\t' * tab, c)
                recurse(c, tab + 1)
        recurse(self, 0)
