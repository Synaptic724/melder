from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellState(Enum):
    """
    Fine-grained state flags for a spell index.

    These are orthogonal markers explaining **why** an index is in a
    particular validity state, and what kind of follow-up work is needed.

    Contract:
    - These flags do not replace `SpellValidity`; they explain the reason a
      index is gated, invalid, quarantined, or otherwise notable.
    - Multiple flags may be present on the same index at once because
      topology, contract, mutation, and ops concerns can overlap.
    - Flag lifecycle is owned by the subsystem that set the flag. Validation
      clears only topology-driven dirt flags; contract, mutation, and ops flags
      must be flipped by their own control-plane logic.

    Threading:
        Immutable enum members; safe to read from any thread. Flags are held as
        a set on `SpellSystemState` and mutated through the owning registry.

    Registration:
        MELDER KERNEL - guarded, readable by value. Control-plane vocabulary.

    Subsystem Context:
        The EXPLANATION axis of the three-axis validity model, between
        `SpellValidity` (the coarse gate meld reads) and
        `SpellStateChangeReason` (the single latest triggering event). Flags are
        the only one of the three that accumulates.

    System Context:
        Multiple simultaneous flags are the normal case, not an edge case, and
        that is why this is a flag SET rather than a status field: topology,
        contract, mutation, and ops concerns genuinely overlap on one lineage.
        A spell can be dependency-dirty AND awaiting a contract provider at the
        same time, and collapsing that into one value would force the control
        plane to pick which truth to discard.
        The lifecycle rule is the operational trap worth reading twice.
        Validation clears ONLY topology-driven dirt flags - it deliberately does
        not touch contract, mutation, or ops flags, because it has no authority
        over those conditions and clearing them would silently forge a verdict
        the owning subsystem never gave. Whoever sets a flag owns clearing it.
        Some advanced flags (`contract_violation`, `mutation_candidate`,
        `mutation_quarantined`, `mutation_failed`) currently have NO producers
        in `src/melder`: they belong to the MutationResearch runtime-seam slice
        that deliberately defers select/staged/promoted acts until the
        notch/bind_inactive seams are real. They are vocabulary awaiting a
        producer, not dead values.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Fine-grained state flags for a spell index. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__ = _mrg.sentinel
    # Topology / graph-level
    new_index = auto()             # first time we see this index
    structure_changed = auto()       # profile / wiring changed
    dependencies_changed = auto()    # direct deps set changed
    impacted_by_dependency = auto()  # downstream of something that changed

    # Contracts / sockets / mutation
    contract_unvalidated = auto()    # has SpellContracts; needs a pass
    contract_violation = auto()      # contract failed; usually -> invalid
    mutation_candidate = auto()      # current version comes from MutationLab
    mutation_quarantined = auto()    # candidate exists but not allowed in prod
    mutation_failed = auto()         # last mutation release failed

    # Ops / incidents / policy
    has_open_incident = auto()       # critical/blocking incident open
    anchored_component = auto()      # infra / non-mutable component
    config_missing = auto()          # required config not present
    transfer_in_progress = auto()    # ownership transfer is actively blocking resolution
