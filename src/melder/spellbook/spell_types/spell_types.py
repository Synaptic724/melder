from enum import Enum, auto

class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    #Classes
    normal = auto()
    normal_with_protocol = auto()
    named = auto()
    named_with_protocol = auto()
    created = auto()
    created_with_protocol = auto()

    #Methods
    normal_method = auto()
    named_method = auto()
    named_lambda_method = auto()

    def __str__(self):
        return self.name