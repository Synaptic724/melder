from enum import Enum, auto



class SocketKind(Enum):
    """
    Internal

    Classify the socket kind represented by a DAG edge.

    This enum now covers only the live compiler socket families:

    - NORMAL:
        Regular DI parameter (annotation, SpellMap, etc.).
    - SPELL_CONTRACT:
        A SpellContract socket that must be satisfied by a provider spell.
    - OVERRIDE_REQUIRED:
        A required input whose selected registration is non-resolvable. Its
        target is descriptive; a caller supplies the value during construction.
    - UNRESOLVED_INPUT:
        A single typed dependency that no registered spell provides. Resolution
        records it instead of failing: it has no target and no DAG edge, the
        constructing call must supply the value through its override payload,
        and a missing value raises `UnresolvedInputError` when that object is
        built. Registering a matching provider later re-resolves the consumer
        and the socket becomes NORMAL. Distinct from OVERRIDE_REQUIRED, which is
        produced only by a registered non-resolvable definition.

    Subsystem Context:
        The edge-kind vocabulary of the `dag` package: a DAG socket carries one of
        these to say whether it is a normal DI edge or a late-bound contract edge.

    System Context:
        Phase 3 (local frame / DAG) of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-3 DAG edge classifier: NORMAL (regular DI socket) vs
        SPELL_CONTRACT (late-bound provider socket), OVERRIDE_REQUIRED (required supplied input),
        UNRESOLVED_INPUT (typed dependency with no provider; supplied by the call or reported).
    """

    NORMAL = auto()
    SPELL_CONTRACT = auto()
    OVERRIDE_REQUIRED = auto()
    UNRESOLVED_INPUT = auto()
