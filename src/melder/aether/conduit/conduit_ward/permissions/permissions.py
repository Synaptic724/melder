from enum import Enum, auto

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    NOT_SET = auto()
    READ = auto()
    WRITE = auto()
