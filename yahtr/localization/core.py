import gettext
import locale


class LocStr:
    def __init__(self, key):
        self.key = key
        self.loc = None  # lazy init

    def __str__(self):
        if not self.loc:
            self.loc = _(self.key)
            self.__str__ = lambda self: self.loc
        return self.loc

    def __repr__(self):
        return '[{}]:{}'.format(self.key, self.loc)


def init():
    locale.setlocale(locale.LC_ALL, '')  # use user's preferred locale
    loc = locale.getlocale()
    loc_code = loc[0][0:2]  # take first two characters of country code
    filename = 'data/loc/yahtr_{0!s}.mo'.format(loc_code)

    try:
        trans = gettext.GNUTranslations(open(filename, "rb"))
    except IOError:
        trans = gettext.NullTranslations()

    trans.install()

    print(f'[{loc_code}] Localization loaded')
