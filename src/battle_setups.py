import data_loader


class BattleSetup:
    def __init__(self, name, data):
        self.name = name
        self.data = data


def load_all(root_path):
    raw_data = data_loader.local_load(root_path + 'data/battle_setups/', '.json')
    return [BattleSetup(name, data) for name, data in raw_data.items()]
