from enum import Enum, auto

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SocketKind(Enum):
    """
    Internal

    Classify the socket kind represented by a DAG edge.

    This enum now covers only the live compiler socket families:

    - NORMAL:
        Regular DI parameter (annotation, SpellMap, etc.).
    - SPELL_CONTRACT:
        A SpellContract socket that must be satisfied by a provider spell.
    """

    __melder_internal__ = _mrg.sentinel
    NORMAL = auto()
    SPELL_CONTRACT = auto()
