from enum import Enum, auto


class SpellStateChangeReason(Enum):
    """
    Last event that *changed* the state of a lineage.

    This is a single, coarse-grained "why did this change" tag that is easy to
    surface in logs / TOON snapshots / incidents. Detailed context can live in
    SpellSystemState fields (booleans, counters, etc.).
    """

    # Registrations / bindings
    new_lineage = auto()            # first time this lineage was registered
    register_or_rebind = auto()     # new Spell bound to existing lineage

    # Structure / dependency graph
    structure_changed = auto()      # constructor / DI shape / profile changed
    dependencies_changed = auto()   # direct dependency set changed
    dependency_changed = auto()     # one of our deps changed (impact event)
    impacted_by_dependency = auto() # we were marked dirty due to dep changes

    # Contracts
    contract_unvalidated = auto()   # SpellContracts added / changed; needs pass
    contract_violation = auto()     # contract check failed

    # Mutations (version graph)
    mutation_promoted = auto()      # new version promoted to SpellIndex.current
    mutation_rolled_back = auto()   # reverted to a previous version

    # Mutations (MutationContract / overlay)
    mutation_contract_set = auto()      # MutationContract applied / overlay set
    mutation_contract_cleared = auto()  # overlay removed / back to normal
    mutation_failed = auto()            # last mutation run/validation failed
    mutation_candidate = auto()         # lineage now backed by a candidate build
    mutation_quarantined = auto()       # candidate or lineage quarantined

    # Ops / incidents / config
    incident_opened = auto()        # critical incident opened for this lineage
    incident_resolved = auto()      # last known incident resolved
    config_missing = auto()         # required config missing / invalid
    config_supplied = auto()        # config fixed / supplied
    anchored_component = auto()     # marked non-mutable infra component

    # Manual / catch-all
    explicit_mark = auto()          # explicitly marked dirty/attention-needed
    other = auto()                  # anything else; explain in Incident/details
