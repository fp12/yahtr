from yahtr.data.core import DataTemplate


class BattleSetup(DataTemplate):
    __path = 'data/battle_setups/'
    __ext = '.json'

    def __init__(self, file, data):
        self.id = file
        self.data = data

    @staticmethod
    def load_all():
        raw_data = DataTemplate.local_load(BattleSetup.__path, BattleSetup.__ext)
        return [BattleSetup(file, data) for file, data in raw_data.items()]

    @staticmethod
    def load_one(battle_setup_id):
        data = DataTemplate.local_load_single(BattleSetup.__path, battle_setup_id, BattleSetup.__ext)
        if data:
            return BattleSetup(battle_setup_id, data)
        return None
