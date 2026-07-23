import enum


class RecordedUnitState(enum.Enum):
    """
    Recorded lifecycle state for singleton units the record tracks by
    state-switch instead of eviction (MutationResearch, Nexus).

    Purpose:
        A disabled/deactivated singleton keeps its installed configuration,
        so its twin stays in the record and this switch carries the truth
        restore needs. Aether and Crystallizer are deliberately NOT tracked:
        the record itself dies with them, so their state can never outlive
        the profile that would report it.

    Guidance:
        Interpret this enum together with the retained singleton twin. `disabled`
        is not absence: configuration still exists and restore may rebuild then
        deactivate the unit. `cleaned` is terminal recorded intent and prevents
        restore from silently resurrecting a unit whose teardown was observed.
        Do not reuse this enum for ordinary removable twins; their absence is
        represented by eviction/tombstones instead.

    Contract:
        - enabled: the unit is configured and live (`enable()`/`activate()`).
        - disabled: the unit was turned off but keeps its configuration
          (`disable()`/`deactivate()`); the twin remains valid.
        - cleaned: the unit was torn down while the record lived; the twin
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
        deactivate; `cleaned` is terminal recorded intent that forbids restore
        from silently resurrecting a unit whose teardown was observed. Representing
        that as a switch beside a retained twin - rather than a tombstone/eviction,
        which is how ordinary removable twins express absence - is what lets the
        record distinguish "configured but off" from "deliberately destroyed."
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Recorded lifecycle state for singleton units the record tracks by "
        "state-switch instead of eviction (MutationResearch, Nexus). Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    enabled = "enabled"
    disabled = "disabled"
    cleaned = "cleaned"
