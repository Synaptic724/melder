from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    __melder_internal__ = _mrg.sentinel
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
    METHOD_WITH_SPELLFRAME = auto()
    METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    LAMBDA_METHOD_WITH_BINDING_NAME = auto()
    LAMBDA_METHOD_WITH_SPELLFRAME = auto()
    LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME = auto()

    def __str__(self):
        return self.name