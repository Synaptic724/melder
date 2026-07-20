from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellStateChangeReason(Enum):
    """
    Last event that *changed* the state of an index.

    This is a single, coarse-grained "why did this change" tag that is easy to
    surface in logs / TOON snapshots / incidents. Detailed context can live in
    SpellSystemState fields (booleans, counters, etc.).

    Contract:
    - This enum is the coarse companion to `SpellState`: one value captures the
      latest triggering event, while `SpellState` flags capture overlapping
      long-lived conditions.
    - An index typically stores only one active change reason at a time, so
      callers should treat it as a summary of the latest transition rather than
      a full audit history.
    - The subsystem that performs the transition owns choosing the most truthful
      reason value.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Control-plane vocabulary.

    Subsystem Context:
        The EVENT axis of the three-axis validity model, completing
        `SpellValidity` (the gate) and `SpellState` (the accumulating flags).
        It is the axis designed for human and agent consumption - logs, TOON
        snapshots, incidents - rather than for runtime branching.

    System Context:
        This enum is deliberately LOSSY, and knowing that prevents misuse. It
        holds one value at a time and is overwritten by each transition, so it
        is a summary of the latest event, NOT an audit trail. Anything needing
        history must read the journal or the incident record; treating this
        field as a log would silently lose every prior transition.
        That lossiness is affordable precisely because the other two axes are
        not. Flags persist until their owning subsystem clears them and validity
        reflects current truth, so the durable state is intact even though the
        reason is not. The reason exists to answer "what just happened" cheaply
        at a glance, which is the question an operator or agent asks first.
        Mutation overlays are the live producers worth knowing about:
        `Spell.apply_mutation_override` and `clear_mutation_override` emit
        `mutation_contract_set` / `mutation_contract_cleared` even though the
        runtime `MutationContract` descriptor itself is gone and Phase 4 blocks
        that socket family.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Last event that *changed* the state of an index. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__ = _mrg.sentinel
    # Registrations / bindings
    new_index = auto()            # first time this index was registered
    register_or_rebind = auto()     # new Spell bound to existing index

    # Structure / dependency graph
    structure_changed = auto()      # constructor / DI shape / profile changed
    dependencies_changed = auto()   # direct dependency set changed
    dependency_changed = auto()     # one of our deps changed (impact event)
    impacted_by_dependency = auto() # we were marked dirty due to dep changes

    # Contracts
    contract_unvalidated = auto()   # SpellContracts added / changed; needs pass
    contract_violation = auto()     # contract check failed

    # Mutations (version graph)
    mutation_promoted = auto()      # new version promoted to SpellIndex.selected_spell_id
    mutation_rolled_back = auto()   # reverted to a previous version

    # Selection (general, not a mutation)
    selected_different_spell = auto()  # notch repointed the index to a different existing member

    # Mutations (MutationContract / overlay)
    mutation_contract_set = auto()      # MutationContract applied / overlay set
    mutation_contract_cleared = auto()  # overlay removed / back to normal
    mutation_failed = auto()            # last mutation run/validation failed
    mutation_candidate = auto()         # index now backed by a candidate build
    mutation_quarantined = auto()       # candidate or index quarantined

    # Validation
    validation_passed = auto()       # latest validation cycle succeeded
    validation_failed = auto()       # validation surfaced errors / gating

    # Ops / incidents / config
    incident_opened = auto()        # critical incident opened for this index
    incident_resolved = auto()      # last known incident resolved
    config_missing = auto()         # required config missing / invalid
    config_supplied = auto()        # config fixed / supplied
    anchored_component = auto()     # marked non-mutable infra component
    transfer_in_progress = auto()   # ownership transfer gate

    # Disposal
    cleaned_up_spell = auto()       # owning spell disposed via cleanup_spell

    # Manual / catch-all
    explicit_mark = auto()          # explicitly marked dirty/attention-needed
    other = auto()                  # anything else; explain in Incident/details
