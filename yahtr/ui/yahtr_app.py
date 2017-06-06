from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from yahtr.ui.screens.main_menu import MainMenu
from yahtr.ui.screens.credits import Credits


class YAHTRApp(App):
    def __init__(self, mode, **kwargs):
        super(YAHTRApp, self).__init__(**kwargs)
        self.screen_manager = ScreenManager(transition=FadeTransition())
        self.mode = mode

    def build(self):
        self.title = 'Yet Another Hex Tactical RPG'

        main_menu = MainMenu(name='main_menu')
        self.screen_manager.add_widget(main_menu)
        self.screen_manager.add_widget(Credits(name='credits'))

        if self.mode == 'chess_demo':
            main_menu.on_go_to_chess_demo()
        elif self.mode == 'editor':
            main_menu.on_go_to_editor()

        return self.screen_manager
