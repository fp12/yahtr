from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

from ui.game_view import GameView
from ui.class_list import create_class_list
from ui.timed_widget import TimedWidgetBar
from ui.actions_bar import ActionsBar

from game import game_instance
from player import Player
from unit import Unit
from hex_lib import Hex


class MainWindow(App):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self._layout = None
        self.game_view = None
        self.time_bar = TimedWidgetBar(max_widgets=10, size_hint=(None, 1), width=100)
        self.actions_bar = ActionsBar()
        self._key_binder = {}
        Window.bind(on_key_down=self._on_keyboard_down)

    def on_unit_selected(self, adapter, *args):
        if len(adapter.selection) == 1:
            selected_class = adapter.selection[0].text
            if selected_class in game_instance.classes.keys():
                self.game_view.spawn_unit(selected_class)

    def on_start(self):
        # prepare UI
        game_instance.load()
        self.game_view = GameView(pos=(0, 0), size_hint=(None, None), size=Window.size)
        self._layout.add_widget(self.game_view)
        list_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        list_layout.add_widget(create_class_list(game_instance.classes, self.on_unit_selected))
        self._layout.add_widget(list_layout)

        anchor_tr = AnchorLayout(anchor_x='right', anchor_y='top')
        anchor_tr.add_widget(self.time_bar)
        self._layout.add_widget(anchor_tr)

        anchor_bc = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(0.3, 0.05))
        anchor_bc.add_widget(self.actions_bar)
        self._layout.add_widget(anchor_bc)

        # prepare fight
        p1 = Player('Player 1')
        p2 = Player('Player 2')
        game_instance.register_player(p1)
        game_instance.register_player(p2)
        game_instance.start_new_fight(fight_map='hexagon_default', players=[p1, p2])
        self.game_view.load_map()

        # deployment
        u11 = Unit('guard')
        u12 = Unit('lancer')
        u21 = Unit('rogue')
        u22 = Unit('warrior')

        p1.add_unit(u11)
        p1.add_unit(u12)
        p1.add_unit(u21)
        p1.add_unit(u22)

        u11.move_to(hex_coords=Hex(-1, -4), orientation=Hex(0,  1))
        u12.move_to(hex_coords=Hex( 1, -5), orientation=Hex(0,  1))
        u21.move_to(hex_coords=Hex(-1,  5), orientation=Hex(0, -1))
        u22.move_to(hex_coords=Hex( 1,  4), orientation=Hex(0, -1))

        game_instance.deployment_finished({p1: [u11, u12], p2: [u21, u22]})  # see ordered dict
        self.game_view.load_squads()
        self.time_bar.create()
        self.actions_bar.create()
        self.actions_bar.register_event(on_action_change=self.game_view.on_action_change)

        self._key_binder.update({'d': [self.game_view.on_debug_key],
                                 'n': [game_instance.current_fight.time_bar.next],
                                 '0': [lambda: self.actions_bar.on_key_pressed('0')],
                                 '1': [lambda: self.actions_bar.on_key_pressed('1')],
                                 '2': [lambda: self.actions_bar.on_key_pressed('2')],
                                 '3': [lambda: self.actions_bar.on_key_pressed('3')],
                                 '4': [lambda: self.actions_bar.on_key_pressed('4')],
                                 })

    def build(self):
        self._layout = FloatLayout()
        self.title = 'Yet Another Hex Tactical RPG'
        return self._layout

    def _on_keyboard_down(self, sdl_thing, code, thing, key, modifiers, *args):
        if key in self._key_binder:
            for cb in self._key_binder[key]:
                cb()
            return True
