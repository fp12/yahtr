import yahtr.localization.core
yahtr.localization.core.init()

from yahtr.game_data import game_data


def main():
    game_data.load_all()

    with open('data/loc/yahtr.pot', 'a') as fp:
        for sk in game_data.skills:
            print('#: data\\{}:name'.format(sk.id), file=fp)
            print('msgid "{}"'.format(sk.name), file=fp)
            print('msgstr ""\n', file=fp)
            print('#: data\\{}:description'.format(sk.id), file=fp)
            print('msgid "{}"'.format(sk.description), file=fp)
            print('msgstr ""\n', file=fp)

        for w in game_data.weapons_templates:
            print('#: data\\{}:name'.format(w.id), file=fp)
            print('msgid "{}"'.format(w.name), file=fp)
            print('msgstr ""\n', file=fp)
            print('#: data\\{}:description'.format(w.id), file=fp)
            print('msgid "{}"'.format(w.description), file=fp)
            print('msgstr ""\n', file=fp)

        for u in game_data.units_templates:
            print('#: data\\{}:name'.format(u.id), file=fp)
            print('msgid "{}"'.format(u.name), file=fp)
            print('msgstr ""\n', file=fp)
            print('#: data\\{}:description'.format(u.id), file=fp)
            print('msgid "{}"'.format(u.description), file=fp)
            print('msgstr ""\n', file=fp)


if __name__ == '__main__':
    main()
