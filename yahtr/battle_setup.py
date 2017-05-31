from yahtr.data_loader import local_load


class BattleSetup:
    def __init__(self, file, data):
        self.id = file
        self.data = data


def load_all(root_path):
    raw_data = local_load(root_path + 'data/battle_setups/', '.json')
    return [BattleSetup(file, data) for file, data in raw_data.items()]
