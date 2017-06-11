from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from yahtr.ui.screens.game_screen import GameScreen
from yahtr.ui.screens.editor import Editor

from yahtr.game_data import game_data

Builder.load_file('yahtr/ui/kv/main_menu.kv')


class MainMenu(Screen):
    def on_go_to_features_demo(self):
        options = {'setup_name': 'features_demo'}
        game_screen = GameScreen(battle_options=options, name='game_screen')
        self.manager.switch_to(game_screen)

    def on_go_to_chess_demo(self):
        options = {'setup_name': 'chess_demo'}
        game_screen = GameScreen(battle_options=options, name='game_screen')
        self.manager.switch_to(game_screen)

    def on_go_to_editor(self):
        game_data.load_all()
        editor = Editor()
        self.manager.switch_to(editor)
