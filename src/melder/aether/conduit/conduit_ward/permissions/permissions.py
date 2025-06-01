from enum import Enum, auto

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    not_set = auto()
    read = auto()
    write = auto()
