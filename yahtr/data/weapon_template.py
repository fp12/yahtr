from enum import Enum

from yahtr.data.core import DataTemplate
from yahtr.localization.core import LocStr
from yahtr.utils import attr


class WeaponType(Enum):
    sword = 1
    daggers = 2
    spear = 3
    scythe = 4
    grimoire = 5


class WeaponTemplate(DataTemplate):
    """ Weapon as defined in data """

    __path = 'data/templates/weapons/'
    __ext = '.json'

    __attributes = []

    def __init__(self, file_id, data, get_skill, **kwargs):
        super(WeaponTemplate, self).__init__(file_id, **kwargs)
        attr.get_from_dict(self, data, *WeaponTemplate.__attributes)
        self.wp_type = WeaponType[data['type']]
        self.skills = [get_skill(s, parent=self) for s in data['skills']] if 'skills' in data else []

        self.name = LocStr(self.loc_key_name)
        self.description = LocStr(self.loc_key_desc)

    def __repr__(self):
        return f'WpTp<{self.name!s}>'

    @property
    def loc_key_name(self):
        return 'L_WEAPON_NAME/{0}'.format(self.file_id.replace('\\', '/'))

    @property
    def loc_key_desc(self):
        return 'L_WEAPON_DESC/{0}'.format(self.file_id.replace('\\', '/'))

    @staticmethod
    def load_all(get_skill, **kwargs):
        raw_weapons = DataTemplate.local_load(WeaponTemplate.__path, WeaponTemplate.__ext)
        return [WeaponTemplate(file, data, get_skill, **kwargs) for file, data in raw_weapons.items()]

    @staticmethod
    def load_one(weapon_template_id, get_skill, **kwargs):
        data = DataTemplate.local_load_single(WeaponTemplate.__path, weapon_template_id, WeaponTemplate.__ext)
        if data:
            return WeaponTemplate(weapon_template_id, data, get_skill, **kwargs)
        return None
