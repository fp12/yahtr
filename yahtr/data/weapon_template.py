from enum import Enum

from yahtr.data.core import DataTemplate
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

    __attributes = ['name', 'description']

    def __init__(self, file, data, get_skill):
        self.id = file
        attr.get_from_dict(self, data, *WeaponTemplate.__attributes)
        self.wp_type = WeaponType[data['type']]
        self.skills = [get_skill(s) for s in data['skills']] if 'skills' in data else []

    def __repr__(self):
        return f'WpTp<{self.name}>'

    @staticmethod
    def load_all(get_skill):
        raw_weapons = DataTemplate.local_load(WeaponTemplate.__path, WeaponTemplate.__ext)
        return [WeaponTemplate(file, data, get_skill) for file, data in raw_weapons.items()]

    @staticmethod
    def load_one(weapon_template_id, get_skill):
        data = DataTemplate.local_load_single(WeaponTemplate.__path, weapon_template_id, WeaponTemplate.__ext)
        if data:
            return WeaponTemplate(weapon_template_id, data, get_skill)
        return None
