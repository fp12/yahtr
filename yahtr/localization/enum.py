from enum import Enum

from yahtr.localization.core import LocStr


class LocalizedEnum(Enum):
    def __init__(self, __):
        self.loc_str = LocStr(self.name)

    def __str__(self):
        return str(self.loc_str)
