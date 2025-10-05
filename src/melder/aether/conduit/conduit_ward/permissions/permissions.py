from enum import Enum, auto

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    read = auto() # Allows reading data
    create = auto() # Allows creating new data, and includes read
    block = auto() # Allows blocking data, used only within Spellbook
