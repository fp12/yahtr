import localization.core
localization.core.init()

import kivy
kivy.require('1.10.0')

from ui.main_window import MainWindow


if __name__ == '__main__':
    MainWindow().run()
