from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from ui.game_screen import GameScreen


Builder.load_file('yahtr/ui/kv/main_menu.kv')


class MainMenu(Screen):
    def on_go_to_chess_demo(self):
        options = {'setup_name': 'chess_demo'}
        game_screen = GameScreen(battle_options=options, name='game_screen')
        self.manager.switch_to(game_screen)
