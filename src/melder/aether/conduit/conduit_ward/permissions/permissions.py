from enum import Enum, auto

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    read = auto()
    create = auto()
    block = auto()
