from enum import StrEnum
from typing import Any, Optional



class SocketKind(StrEnum):
    """
    Internal

    Classify the socket kind represented by a DAG edge.

    Values exactly match member names. Historical numeric values 1-5 remain
    readable by value and are projected explicitly for numeric compiler rows.

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
    - AMBIGUOUS_INPUT:
        A single typed dependency that two or more registered resolvable spells
        provide (2026-10-04). Resolution records it instead of raising: no
        target, no DAG edge, the candidates kept as descriptive
        `referenced_spell_ids`, and the dependency_key kept so a bind or removal
        of a same-keyed spell re-gates the consumer. Phase 4 refuses the spell
        with AMBIGUOUS_PROVIDER, naming every candidate's address and the
        remedies (a SpellMap default, a meld override, or one provider). Never
        reaches planning: a broken spell does not plan.

    Subsystem Context:
        The edge-kind vocabulary of the `dag` package: a DAG socket carries one of
        these to say whether it is a normal DI edge or a late-bound contract edge.

    System Context:
        Phase 3 (local frame / DAG) of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-3 DAG edge classifier: NORMAL (regular DI socket) vs
        SPELL_CONTRACT (late-bound provider socket), OVERRIDE_REQUIRED (required supplied input),
        UNRESOLVED_INPUT (typed dependency with no provider; supplied by the call or reported),
        AMBIGUOUS_INPUT (typed dependency with several providers; refused by Phase 4 with the candidates).
    """

    NORMAL = "NORMAL"
    SPELL_CONTRACT = "SPELL_CONTRACT"
    OVERRIDE_REQUIRED = "OVERRIDE_REQUIRED"
    UNRESOLVED_INPUT = "UNRESOLVED_INPUT"
    AMBIGUOUS_INPUT = "AMBIGUOUS_INPUT"

    @classmethod
    def _missing_(cls, value: object) -> Optional[SocketKind]:
        """
        Resolve a historical numeric socket kind to its original member.

        Values equal to the old integers remain readable; unknown or unhashable
        inputs return None so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, SocketKind] = {
            1: cls.NORMAL,
            2: cls.SPELL_CONTRACT,
            3: cls.OVERRIDE_REQUIRED,
            4: cls.UNRESOLVED_INPUT,
            5: cls.AMBIGUOUS_INPUT,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None

    @classmethod
    def _legacy_code(cls, value: Any) -> Any:
        """
        Return the historical integer for a SocketKind used in compiler rows.

        Other value-bearing objects retain their prior .value behavior; a missing
        .value raises AttributeError for the caller's existing fallback to handle.
        """
        if value is cls.NORMAL:
            return 1
        if value is cls.SPELL_CONTRACT:
            return 2
        if value is cls.OVERRIDE_REQUIRED:
            return 3
        if value is cls.UNRESOLVED_INPUT:
            return 4
        if value is cls.AMBIGUOUS_INPUT:
            return 5
        return value.value
