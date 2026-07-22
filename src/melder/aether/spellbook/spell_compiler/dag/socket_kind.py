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

    Registration:
        MELDER KERNEL - guarded. A compiler classification enum; not a
        user-bindable value.

    Subsystem Context:
        The edge-kind vocabulary of the `dag` package: a DAG socket carries one of
        these to say whether it is a normal DI edge or a late-bound contract edge.

    System Context:
        Phase 3 (local frame / DAG) of the conjure pipeline.
    """

    __melder_internal__ = _mrg.sentinel
    __ast_helper_access__ = "internal"
    __agent_purpose__ = (
        "access: internal. Phase-3 DAG edge classifier: NORMAL (regular DI socket) vs "
        "SPELL_CONTRACT (late-bound provider socket). Two live socket families only."
    )
    NORMAL = auto()
    SPELL_CONTRACT = auto()
