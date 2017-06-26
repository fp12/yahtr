from yahtr.data.core import DataTemplate


class BattleSetup(DataTemplate):
    __path = 'data/battle_setups/'
    __ext = '.json'

    def __init__(self, file_id, data, **kwargs):
        super(BattleSetup, self).__init__(file_id, **kwargs)
        self.data = data

    @staticmethod
    def load_all(**kwargs):
        raw_data = DataTemplate.local_load(BattleSetup.__path, BattleSetup.__ext)
        return [BattleSetup(file, data, **kwargs) for file, data in raw_data.items()]

    @staticmethod
    def load_one(battle_setup_id, **kwargs):
        data = DataTemplate.local_load_single(BattleSetup.__path, battle_setup_id, BattleSetup.__ext)
        if data:
            return BattleSetup(battle_setup_id, data, **kwargs)
        return None
