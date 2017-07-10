from yahtr.data.bank import data_bank


def main():
    data_bank.load_all()

    with open('data/loc/yahtr.pot', 'a') as fp:
        for sk in data_bank.skills:
            print(f'#: data/skill/{sk.file_id}:name', file=fp)
            print(f'msgid "{sk.loc_key_name}"', file=fp)
            print(f'msgstr ""\n', file=fp)
            print(f'#: data/skill/{sk.file_id}:description', file=fp)
            print(f'msgid "{sk.loc_key_desc}"', file=fp)
            print(f'msgstr ""\n', file=fp)
        print('Skills loc keys added')

        for w in data_bank.weapon_templates:
            print(f'#: data/weapon/{w.file_id}:name', file=fp)
            print(f'msgid "{w.loc_key_name}"', file=fp)
            print(f'msgstr ""\n', file=fp)
            print(f'#: data/weapon/{w.file_id}:description', file=fp)
            print(f'msgid "{w.loc_key_desc}"', file=fp)
            print(f'msgstr ""\n', file=fp)
        print('Weapons loc keys added')

        for u in data_bank.unit_templates:
            print(f'#: data/unit/{u.file_id}:name', file=fp)
            print(f'msgid "{u.loc_key_name}"', file=fp)
            print(f'msgstr ""\n', file=fp)
            print(f'#: data/unit/{u.file_id}:description', file=fp)
            print(f'msgid "{u.loc_key_desc}"', file=fp)
            print(f'msgstr ""\n', file=fp)
        print('Units loc keys added')


if __name__ == '__main__':
    main()
