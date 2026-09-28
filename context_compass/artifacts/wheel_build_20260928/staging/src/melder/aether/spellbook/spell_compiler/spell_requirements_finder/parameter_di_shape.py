from enum import Enum, auto

class ParameterDIShape(Enum):
    """
    High-level classification of how a single parameter is expected to be
    satisfied during resolution.

    This is a **Phase 1 artifact** - it does not perform lookups or graph
    building; it just describes what the parameter *wants*.

    Values
    ------

    IGNORE
        Parameter is not part of DI at all (e.g. "self", "cls", "*args",
        ``**kwargs``). Resolution never tries to satisfy it.

    PLAIN
        Regular argument. No DI contract is implied. Caller/root override or
        default value is expected to satisfy it.

    SINGLE_BY_ANNOTATION
        DI by a **single type annotation** (class, Protocol, interface-like
        type). Phase 2 will decide whether this is a concrete class vs
         spellframe and how to map it to a spell_id.

    COLLECTION_BY_ANNOTATION
        DI by **collection of implementations**, e.g. "list[IMyHandler]".
        The element annotation indicates the frame/type whose implementations
        should be gathered.

    SPELLMAP_DEFAULT
        Parameter default is a: class:`SpellMap`. This is a fully explicit DI
        descriptor and has priority over plain annotations.

    SPELL_CONTRACT
        Parameter default is a: class:`SpellContract`. This indicates that
        the parameter expects a single resolved spell matching the contract.

    Registration:
        MELDER KERNEL - guarded. A Phase-1 classification enum owned by the
        compiler; it is not a user-bindable value. (The dunder attributes below
        are class attributes, not enum members, so they do not widen the value
        set.)

    Subsystem Context:
        The vocabulary the `spell_requirements_finder` package speaks: each
        `SpellParameterRequirement` carries exactly one of these shapes, and
        `SpellRequirements.iter_di_parameters()` selects on them. It captures what
        a parameter WANTS before any lookup happens.

    System Context:
        Decided in Phase 1 (requirements extraction) of the conjure pipeline,
        upstream of the symbolic graph (Phase 2), the local frame/DAG (Phase 3),
        and validation (Phase 4). Nothing here touches the Spellbook or the live
        object world.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-1 enum classifying how one parameter wants to be satisfied:
        IGNORE / PLAIN / SINGLE_BY_ANNOTATION / COLLECTION_BY_ANNOTATION / SPELLMAP_DEFAULT /
        SPELL_CONTRACT. Describes intent only - it performs no lookups.
    """
    IGNORE = auto()
    PLAIN = auto()
    SINGLE_BY_ANNOTATION = auto()
    COLLECTION_BY_ANNOTATION = auto()
    SPELLMAP_DEFAULT = auto()
    SPELL_CONTRACT = auto()
