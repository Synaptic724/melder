from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    __melder_internal__ = _mrg.sentinel
    read = auto() # Allows reading data
    create = auto() # Allows creating new data, and includes read
    block = auto() # Allows blocking data, used only within Spellbook
