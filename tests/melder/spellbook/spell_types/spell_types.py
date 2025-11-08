from enum import Enum, auto

class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    #Classes
    NORMAL = auto()
    NORMAL_INTERFACED = auto()
    NAMED = auto()
    NAMED_INTERFACED = auto()
    EXISTING_CLASS = auto()
    EXISTING_INTERFACED_CLASS = auto()

    #Methods
    NORMAL_METHOD = auto()
    NAMED_METHOD = auto()
    NAMED_LAMBDA_METHOD = auto()

    def __str__(self):
        return self.name