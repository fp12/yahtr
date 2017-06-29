import logging
import logging.handlers

from yahtr.utils.event import Event


class GameConsoleHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.on_message = Event('message')

    def emit(self, record):
        msg = self.format(record)
        # Broadcast the formatted record
        self.on_message(msg)


class MarkupFormatter(logging.Formatter):
    level_colors = {
        logging.DEBUG: '222222',
        logging.INFO: '999999',
        logging.WARNING: '991111',
        logging.ERROR: '991111',
        }

    def format(self, record):
        s = super(MarkupFormatter, self).format(record)
        s = ''.join(['[color={}]'.format(self.level_colors[record.levelno]), s, '[/color]'])
        return s


# Main
main_formatter = logging.Formatter(fmt='[%(module)-12s][%(levelname)s] %(message)s')

main_handler = logging.StreamHandler()
main_handler.setFormatter(main_formatter)


# Markup
markup_formatter = MarkupFormatter(fmt='[%(module)-12s] %(message)s')

game_console_handler = GameConsoleHandler()
game_console_handler.setFormatter(markup_formatter)
game_console_handler.setLevel(logging.INFO)


# getting root logger child so it can work along with kivy's logging system
log_main = logging.getLogger().getChild('MAIN')
log_main.setLevel(logging.DEBUG)
log_main.addHandler(main_handler)
log_main.propagate = False  # don't propagate to kivy's logging system


# System logging
log_system = log_main.getChild('SYSTEM')


def create_system_logger(name):
    return log_system.getChild(name)


# Game logging
log_game = log_main.getChild('GAME')
log_game.addHandler(game_console_handler)


def create_game_logger(name):
    return log_game.getChild(name)


# UI logging
log_ui = log_main.getChild('UI')
log_ui.addHandler(game_console_handler)


def create_ui_logger(name):
    return log_ui.getChild(name)
