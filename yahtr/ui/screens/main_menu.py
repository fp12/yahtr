from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


Builder.load_file('yahtr/ui/kv/main_menu.kv')


class MainMenu(Screen):
    screen_name = 'main_menu'

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(name=MainMenu.screen_name, **kwargs)
