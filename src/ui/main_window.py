from collections import OrderedDict
import threading

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock

from ui.game_view import GameView
from ui.timed_widget import TimedWidgetBar
from ui.actions_bar import ActionsBar
from ui.anim_scheduler import AnimScheduler

from game import game_instance
from player import Player
from player_ai import PlayerAI
from unit import Unit
import tie
from core.hex_lib import Hex


Builder.load_file('src/ui/kv/main_window.kv')


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

        self.layout = None
        self.game_view = None
        self.time_bar = None
        self.actions_bar = None
        self._key_binder = {}
        self.anim_scheduler = AnimScheduler()

        Window.bind(on_key_down=self.on_keyboard_down, mouse_pos=self.on_mouse_pos)

    def on_start(self):
        # prepare game logic
        game_instance.load()

        # prepare UI
        self.time_bar = TimedWidgetBar(pos=(Window.width / 2 - 60, 75), size_hint=(None, 1), width=75)
        self.layout.add_widget(self.time_bar, 0)

        self.actions_bar = ActionsBar(pos=self.time_bar.get_pos_for_actions_bar(), size_hint=(None, None))
        self.layout.add_widget(self.actions_bar, 1)

        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size, auto_bring_to_front=False)
        self.layout.add_widget(self.game_view, 2)

        # prepare fight
        p1 = Player(game_instance, 'Player')
        p2 = PlayerAI(game_instance, 'AI')

        game_instance.prepare_new_fight(fight_map='demo_map', players=[p1, p2])
        game_instance.current_fight.set_tie(p1, p2, tie.Type.Enemy)
        game_instance.current_fight.on_skill_turn += self.on_fight_skill_turn

        self.game_view.load_map()

        # deployment
        w11 = p1.add_weapon('default_sword')
        w12 = p1.add_weapon('default_grimoire')
        w21 = p2.add_weapon('default_daggers')
        w22 = p2.add_weapon('default_sword')
        w31 = p1.add_weapon('default_scythe')

        u11 = Unit(game_instance.get_unit_template('reaper'))
        u12 = Unit(game_instance.get_unit_template('guard'))
        u21 = Unit(game_instance.get_unit_template('rogue'))
        u22 = Unit(game_instance.get_unit_template('white_mage'))

        u11.equip(w31)
        u12.equip(w11)
        u21.equip(w21)
        u22.equip(w12)

        p1.add_unit(u11)
        p1.add_unit(u12)
        p2.add_unit(u21)
        p2.add_unit(u22)

        u11.move_to(hex_coords=Hex(-1, -4), orientation=Hex(0,  1))
        u12.move_to(hex_coords=Hex( 1, -5), orientation=Hex(0,  1))
        u21.move_to(hex_coords=Hex(-1,  5), orientation=Hex(0, -1))
        u22.move_to(hex_coords=Hex( 1,  4), orientation=Hex(0, -1))

        squads = OrderedDict()
        squads.update({p1: [u11, u12]})
        squads.update({p2: [u21, u22]})
        game_instance.current_fight.deploy(squads)

        self.game_view.load_squads()
        self.time_bar.create()
        self.actions_bar.create()

        self._key_binder.update({'q': [self.game_view.on_debug_key],
                                 'shift+=': [self.game_view.on_zoom_down],
                                 '+': [self.game_view.on_zoom_down],
                                 '-': [self.game_view.on_zoom_up],
                                 'a': [self.game_view.on_move_key],
                                 's': [self.game_view.on_move_key],
                                 'd': [self.game_view.on_move_key],
                                 'w': [self.game_view.on_move_key],
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

        game_instance.current_fight.start()

        Clock.schedule_interval(game_instance.update, 1 / 30.)

    def on_fight_skill_turn(self):
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
        if code in self._key_binder:
            for cb in self._key_binder[code]:
                cb(keycode, code)
            return True

    def on_mouse_pos(self, *args):
        """dispatching mouse position by priority order
        Note: Could be improved..."""
        dispatch_success = self.time_bar.on_mouse_pos(*args)
        if dispatch_success:
            self.actions_bar.on_no_mouse_pos()
            self.game_view.on_no_mouse_pos()
        else:
            dispatch_success = self.actions_bar.on_mouse_pos(*args)
            if dispatch_success:
                self.game_view.on_no_mouse_pos()
            else:
                self.game_view.on_mouse_pos(*args)

    def print_children(self, *args):
        def recurse(w, tab):
            for c in w.children:
                print('\t' * tab, c)
                recurse(c, tab + 1)
        recurse(self.layout, 0)
