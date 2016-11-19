import logging
import logging.handlers

from utils.event import Event


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


markup_formatter = MarkupFormatter(fmt='[%(module)-12s] %(message)s')

game_console_handler = GameConsoleHandler()
game_console_handler.setFormatter(markup_formatter)

# getting root logger child so it can work along with kivy's logging system
log_main = logging.getLogger().getChild('MAIN')
log_main.addHandler(logging.StreamHandler())
log_main.propagate = False  # don't propagate to kivy's logging system

log_game = log_main.getChild('GAME')
log_game.addHandler(game_console_handler)
