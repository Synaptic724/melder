from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellState(Enum):
    """
    Fine-grained state flags for a spell lineage.

    These are orthogonal markers explaining **why** a lineage is in a
    particular validity state, and what kind of follow-up work is needed.

    Contract:
    - These flags do not replace `SpellValidity`; they explain the reason a
      lineage is gated, invalid, quarantined, or otherwise notable.
    - Multiple flags may be present on the same lineage at once because
      topology, contract, mutation, and ops concerns can overlap.
    - Flag lifecycle is owned by the subsystem that set the flag. Validation
      clears only topology-driven dirt flags; contract, mutation, and ops flags
      must be flipped by their own control-plane logic.
    """
    __melder_internal__ = _mrg.sentinel
    # Topology / graph-level
    new_lineage = auto()             # first time we see this lineage
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
