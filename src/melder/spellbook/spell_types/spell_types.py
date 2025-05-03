from enum import Enum, auto

class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    NORMAL = auto()
    NAMED = auto()
    EXISTING_CLASS = auto()
    NORMAL_METHOD = auto()
    NAMED_METHOD = auto()

    def __str__(self):
        return self.name