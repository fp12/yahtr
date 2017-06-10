from yahtr.data_loader import local_load, local_load_single


class BattleSetup:
    def __init__(self, file, data):
        self.id = file
        self.data = data


__path = 'data/battle_setups/'
__ext = '.json'


def load_all_battle_setups():
    raw_data = local_load(__path, __ext)
    return [BattleSetup(file, data) for file, data in raw_data.items()]


def load_one_battle_setup(battle_setup_id):
    data = local_load_single(__path, battle_setup_id, __ext)
    if data:
        return BattleSetup(battle_setup_id, data)
    return None
