import sys
import getopt

from yahtr.game_data import game_data
from yahtr.localization.core import init as init_localization
init_localization()

from yahtr.ui.yahtr_app import YAHTRApp


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '', ['mode='])
    mode = None
    for opt, arg in opts:
        if opt in ('--mode',):
            mode = arg

    # load static data
    game_data.load()

    YAHTRApp(mode).run()
