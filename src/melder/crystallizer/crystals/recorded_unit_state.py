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

    Contract:
        - enabled: the unit is configured and live (enable()/activate()).
        - disabled: the unit was turned off but keeps its configuration
          (disable()/deactivate()); the twin remains valid.
        - cleaned: the unit was torn down while the record lived; the twin
          remains as configured-history, and restore must not re-enable it.

    Threading:
        Enum members are immutable; safe to share across threads.
    """

    enabled = "enabled"
    disabled = "disabled"
    cleaned = "cleaned"
