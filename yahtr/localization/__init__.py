import gettext
from os.path import dirname, join

loc_domain = 'yahtr'
locale_dir = join(dirname(dirname(dirname(__file__))), 'data', 'loc')

gettext.bindtextdomain(loc_domain, locale_dir)
gettext.textdomain(loc_domain)

languages = {}
for lang in ('en', 'fr'):
    languages[lang] = gettext.translation(loc_domain, locale_dir, languages=[lang])

languages['fr'].install()
print('loc init done')
