from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from yahtr.ui.screens.main_menu import MainMenu
from yahtr.ui.screens.credits import Credits
from yahtr.ui.screens.game_screen import GameScreen
from yahtr.ui.screens.editor import Editor

from yahtr.game_data import game_data


class YAHTRApp(App):
    def __init__(self, mode, **kwargs):
        super(YAHTRApp, self).__init__(**kwargs)
        self.screen_manager = ScreenManager(transition=FadeTransition())
        self.mode = mode

    def build(self):
        self.title = 'Yet Another Hex Tactical RPG'

        if self.mode == 'chess_demo':
            self.go_to_chess_demo()
        elif self.mode == 'editor':
            self.go_to_editor()
        else:
            self.go_to_main_menu()

        return self.screen_manager

    def go_to_features_demo(self):
        options = {'setup_name': 'features_demo'}
        game_screen = GameScreen(battle_options=options)
        self.screen_manager.switch_to(game_screen)

    def go_to_chess_demo(self):
        options = {'setup_name': 'chess_demo'}
        game_screen = GameScreen(battle_options=options)
        self.screen_manager.switch_to(game_screen)

    def go_to_editor(self):
        game_data.load_all()
        self.screen_manager.switch_to(Editor())

    def go_to_main_menu(self):
        self.screen_manager.switch_to(MainMenu())

    def go_to_credits(self):
        self.screen_manager.switch_to(Credits())
