from enum import Enum, auto

class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    #Classes
    SPELL = auto()
    SPELL_WITH_SPELLFRAME = auto()
    SPELL_WITH_BINDING_NAME = auto()
    SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()
    # A pre-existing creation object
    # for pre-existing objects spells are created but no dag is created if they are disposed

    EXISTING_CREATION = auto()
    EXISTING_CREATION_WITH_SPELLFRAME = auto()
    EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    #Methods
    METHOD = auto()
    METHOD_WITH_BINDING_NAME = auto()
    LAMBDA_METHOD_WITH_BINDING_NAME = auto()

    def __str__(self):
        return self.name