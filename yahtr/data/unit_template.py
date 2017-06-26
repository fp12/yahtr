from yahtr.core.hex_lib import Hex
from yahtr.data.core import DataTemplate
from yahtr.utils import attr
from yahtr.rank import Rank
from yahtr.skill import RankedSkill


class UnitTemplate(DataTemplate):
    """ Unit as defined in data """

    __path = 'data/templates/units/'
    __ext = '.json'

    __attributes = ['name', 'description', 'move', 'initiative', 'speed', 'shields', 'color', 'weapons', 'health']

    def __init__(self, file_id, data, get_skill, get_actions_tree, **kwargs):
        super(UnitTemplate, self).__init__(file_id, **kwargs)
        attr.get_from_dict(self, data, *UnitTemplate.__attributes)
        self.actions_tree = get_actions_tree(data['actions_tree_name'], parent=self)

        self.skills = [RankedSkill(get_skill(n, parent=self), Rank[rank]) for n, rank in data['skills'].items()] if 'skills' in data else []

        self.shape = [Hex(0, 0)]
        if 'shape' in data:
            self.shape = []
            shape_def = data['shape']
            for index in range(0, len(shape_def), 2):
                self.shape.append(Hex(q=shape_def[index], r=shape_def[index + 1]))

    @staticmethod
    def load_all(get_skill, get_actions_tree, **kwargs):
        raw_units = DataTemplate.local_load(UnitTemplate.__path, UnitTemplate.__ext)
        return [UnitTemplate(file, data, get_skill, get_actions_tree, **kwargs) for file, data in raw_units.items()]

    @staticmethod
    def load_one(unit_template_id, get_skill, get_actions_tree, **kwargs):
        data = DataTemplate.local_load_single(UnitTemplate.__path, unit_template_id, UnitTemplate.__ext)
        if data:
            return UnitTemplate(unit_template_id, data, get_skill, get_actions_tree, **kwargs)
        return None
