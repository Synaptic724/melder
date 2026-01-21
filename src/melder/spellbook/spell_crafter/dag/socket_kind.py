from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class SocketKind(Enum):
    """
    Internal

    Classifies the *kind* of socket represented by a DAG edge.

    This is derived from the DI shape of the underlying parameter:

    - NORMAL:
        Regular DI parameter (annotation, SpellMap, etc.).
    - SPELL_CONTRACT:
        A SpellContract socket – structural contract that must be satisfied
        by a provider spell (possibly from contracted spellbooks).
    - MUTATION_CONTRACT:
        A MutationContract socket – potential mutation site that can be
        rewired at meld-time via mutation overrides.
    """
    __melder_internal__ = _mrg.sentinel
    NORMAL = auto()
    SPELL_CONTRACT = auto()
    MUTATION_CONTRACT = auto()
