from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from ui.main_menu import MainMenu
from ui.credits import Credits


class YAHTRApp(App):
    screen_manager = ScreenManager(transition=FadeTransition())

    def build(self):
        self.title = 'Yet Another Hex Tactical RPG'
        self.screen_manager.add_widget(MainMenu(name='main_menu'))
        self.screen_manager.add_widget(Credits(name='credits'))
        return self.screen_manager
