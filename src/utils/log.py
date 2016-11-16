import logging
import logging.config
import logging.handlers

from utils.event import Event


logging_config = {
        'version': 1,
        'formatters': {
            'detailed_fmt': {
                'class': 'logging.Formatter',
                'format': '[%(name)-12s] %(levelname)-8s %(processName)-10s %(message)s'
            },
            'game_console_fmt': {
                '()': 'utils.log_utils.MarkupFormatter',
                'format': '[%(name)-12s] %(message)s'
            }
        },
        'handlers': {
            'game_console': {
                '()': 'utils.log_utils.GameConsoleHandler',
                'formatter': 'game_console_fmt'
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'yathr': {
                'handlers': ['console']
            },
            'yathr.fight': {
                'handlers': ['console'],
                'level': 'NOTSET',
                'propagate': 0,
            }
        },
        'root': {
            'level': 'NOTSET',
            'handlers': ['console']
        }
    }


class GameConsoleHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.on_message = Event('message')

    def emit(self, record):
        try:
            msg = self.format(record)
            self.on_message(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


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


markup_formatter = MarkupFormatter(fmt='[%(name)-12s] %(message)s')

game_console_handler = GameConsoleHandler()
game_console_handler.setFormatter(markup_formatter)

# getting root logger child so it can work along with kivy's logging system
log_main = logging.getLogger().getChild('yahtr')
log_main.addHandler(logging.StreamHandler())
log_main.propagate = False  # don't propagate to kivy's logging system

log_fight = logging.getLogger().getChild('FIGHT')
log_fight.addHandler(game_console_handler)
