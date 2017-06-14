import sys
import getopt

from yahtr.localization.core import init as init_localization
init_localization()

from yahtr.ui.yahtr_app import YAHTRApp


def main():
    opts, args = getopt.getopt(sys.argv[1:], '', ['mode='])
    mode = None
    for opt, arg in opts:
        if opt in ('--mode',):
            mode = arg

    YAHTRApp(mode).run()


if __name__ == '__main__':
    main()
