from collections import OrderedDict

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

from ui.game_view import GameView
from ui.timed_widget import TimedWidgetBar
from ui.actions_bar import ActionsBar

from game import game_instance
from player import Player
from unit import Unit
import tie
from hex_lib import Hex


Builder.load_file('src/ui/kv/main_window.kv')


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

        self.layout = None
        self.game_view = None
        self.time_bar = None
        self.actions_bar = None
        self._key_binder = {}
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_start(self):
        # prepare game logic
        game_instance.load()

        # prepare UI
        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size)
        self.layout.add_widget(self.game_view)

        self.time_bar = TimedWidgetBar(pos=(Window.width/2 - 60, 75), size_hint=(None, 1), width=75)
        self.layout.add_widget(self.time_bar)

        self.actions_bar = ActionsBar(pos=self.time_bar.get_pos_for_actions_bar(), size_hint=(None, None))
        self.layout.add_widget(self.actions_bar)

        # prepare fight
        p1 = Player(game_instance, 'Player 1')
        p2 = Player(game_instance, 'Player 2')
        game_instance.prepare_new_fight(fight_map='hexagon_default', players=[p1, p2])
        game_instance.current_fight.set_tie(p1, p2, tie.Type.Enemy)
        self.game_view.load_map()

        # deployment
        w11 = p1.add_weapon('default_sword')
        w12 = p1.add_weapon('default_spear')
        w21 = p2.add_weapon('default_daggers')
        w22 = p2.add_weapon('default_sword')

        u11 = Unit(game_instance.get_unit_template('mounted_knight'))
        u12 = Unit(game_instance.get_unit_template('lancer'))
        u21 = Unit(game_instance.get_unit_template('rogue'))
        u22 = Unit(game_instance.get_unit_template('boss'))

        u11.equip(w11)
        u12.equip(w12)
        u21.equip(w21)
        u22.equip(w22)

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

        self._key_binder.update({'d': [self.game_view.on_debug_key],
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

    def build(self):
        self.layout = FloatLayout()
        self.title = 'Yet Another Hex Tactical RPG'
        return self.layout

    def _on_keyboard_down(self, sdl_thing, code, thing, key, modifiers, *args):
        if key in self._key_binder:
            for cb in self._key_binder[key]:
                cb(code, key)
            return True
