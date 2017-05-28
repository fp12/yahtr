import localization.core
localization.core.init()

import kivy
kivy.require('1.10.0')

from ui.yahtr_app import YAHTRApp

from game_data import game_data


if __name__ == '__main__':
    # load static data
    game_data.load()

    YAHTRApp().run()
