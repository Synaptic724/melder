from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ParameterDIShape(Enum):
    """
    High-level classification of how a single parameter is expected to be
    satisfied during resolution.

    This is a **Phase 1 artifact** – it does not perform lookups or graph
    building; it just describes what the parameter *wants*.

    Values
    ------

    IGNORE
        Parameter is not part of DI at all (e.g. ``self``, ``cls``, ``*args``,
        ``**kwargs``). Resolution never tries to satisfy it.

    PLAIN
        Regular argument. No DI contract is implied. Caller/root override or
        default value is expected to satisfy it.

    SINGLE_BY_ANNOTATION
        DI by a **single type annotation** (class, Protocol, interface-like
        type). Phase 2 will decide whether this is a concrete class vs
        spellframe, and how to map it to a spell_id.

    COLLECTION_BY_ANNOTATION
        DI by **collection of implementations**, e.g. ``list[IMyHandler]``.
        The element annotation indicates the frame/type whose implementations
        should be gathered.

    SPELLMAP_DEFAULT
        Parameter default is a :class:`SpellMap`. This is a fully explicit DI
        descriptor and has priority over plain annotations.

    SPELL_CONTRACT
        Parameter default is a :class:`SpellContract`. This indicates that
        the parameter expects a single resolved spell matching the contract.

    MUTATION_CONTRACT
        Parameter default is a :class:`MutationContract`. This indicates that
        the parameter expects a mutation lineage matching the contract.

    """
    __melder_internal__ = _mrg.sentinel
    IGNORE = auto()
    PLAIN = auto()
    SINGLE_BY_ANNOTATION = auto()
    COLLECTION_BY_ANNOTATION = auto()
    SPELLMAP_DEFAULT = auto()
    SPELL_CONTRACT = auto()
    MUTATION_CONTRACT = auto()
