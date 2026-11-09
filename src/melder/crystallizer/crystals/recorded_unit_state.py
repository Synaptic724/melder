import enum
from typing import Optional


class RecordedUnitState(enum.StrEnum):
    """
    Recorded lifecycle state for singleton units the record tracks by
    state-switch instead of eviction (MutationResearch, Nexus).

    Values match member names. The historical lowercase cleaned value remains
    readable by value, including in older enum pickle payloads.

    Purpose:
        A disabled/deactivated singleton keeps its installed configuration,
        so its twin stays in the record and this switch carries the truth
        restore needs. Aether and Crystallizer are deliberately NOT tracked:
        the record itself dies with them, so their state can never outlive
        the profile that would report it.

    Guidance:
        Interpret this enum together with the retained singleton twin. `disabled`
        is not absence: configuration still exists and restore may rebuild then
        deactivate the unit. `CLEANED` is terminal recorded intent and prevents
        restore from silently resurrecting a unit whose teardown was observed.
        Do not reuse this enum for ordinary removable twins; their absence is
        represented by eviction/tombstones instead.

    Contract:
        - enabled: the unit is configured and live (`enable()`/`activate()`).
        - disabled: the unit was turned off but keeps its configuration
          (`disable()`/`deactivate()`); the twin remains valid.
        - CLEANED: the unit was torn down while the record lived; the twin
          remains as configured history, and restore must not re-enable it.

    Threading:
        Enum members are immutable; safe to share across threads.

    Lifecycle / Cleanup:
        None. Enum members are process-lifetime constants.

    Registration:
        MELDER KERNEL - guarded. A value enum stored on a `PersistenceProfile`
        alongside the singleton twins it annotates; never bound.

    Subsystem Context:
        The lifecycle state-switch of the crystal-twin family. For singleton units
        the record tracks by SWITCH rather than eviction (MutationResearch,
        Nexus), the unit's twin stays in the record and this enum carries whether
        it was left enabled, disabled, or cleaned. Aether and Crystallizer are
        deliberately NOT tracked this way - the record itself dies with them, so
        their state can never outlive the profile.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, encoding a
        subtle honesty rule: for a configured singleton, "turned off" is NOT the
        same as "gone." `disabled` keeps configuration so restore can rebuild then
        deactivate; `CLEANED` is terminal recorded intent that forbids restore
        from silently resurrecting a unit whose teardown was observed. Representing
        that as a switch beside a retained twin - rather than a tombstone/eviction,
        which is how ordinary removable twins express absence - is what lets the
        record distinguish "configured but off" from "deliberately destroyed."

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Recorded lifecycle state for singleton units the record tracks by
        state-switch instead of eviction (MutationResearch, Nexus). Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """

    enabled = "enabled"
    disabled = "disabled"
    CLEANED = "CLEANED"

    @classmethod
    def _missing_(cls, value: object) -> Optional[RecordedUnitState]:
        """
        Resolve the historical lowercase terminal value to CLEANED.

        Current values use ordinary enum lookup. Only the exact old string
        remains accepted here; other values return None so construction raises
        the normal ValueError. This preserves old enum pickle payloads.
        """
        if isinstance(value, str) and value == "cleaned":
            return cls.CLEANED
        return None
