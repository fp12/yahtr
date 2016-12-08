import gettext
import locale


def init():
  locale.setlocale(locale.LC_ALL, '')  # use user's preferred locale
  loc = locale.getlocale()
  loc_code = loc[0][0:2]  # take first two characters of country code
  filename = "data/loc/yahtr_%s.mo" % loc_code

  try:
    trans = gettext.GNUTranslations(open( filename, "rb" ) )
  except IOError:
    trans = gettext.NullTranslations()

  trans.install()

  print('[{}] Localization loaded'.format(loc_code))
