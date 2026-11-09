from enum import StrEnum
from typing import Optional


class SpellState(StrEnum):
    """
    Fine-grained state flags for a spell index.

    Values exactly match member names. Historical numeric values 1-14 remain
    readable by value, including in older enum pickle payloads.

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
    - `non_resolvable` is the capability flag. `SpellSystemStates.register_index`
      sets it when the SpellIndex's selected version was bound resolvable=False and
      clears it when a resolvable version (or, with no stated capability, another
      version) is selected. Validation never clears it and it changes no
      validity; its one reader is RiskManager, which leaves a flagged SpellIndex's
      risk out of the Book's validation flag.

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
        contract, mutation, and ops concerns genuinely overlap on one SpellIndex.
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
        `non_resolvable` exists because `unknown` means "work still owed", and a
        resolvable=False definition - an abstract base, a Protocol, a helper
        kept so agents can discover, inspect and version it, whose consumers
        receive the value by override - owes no resolution verdict at all.
        Every meld door refuses such a version before the validation gate, so
        its never-filled verdict says nothing about whether a meld may skip the
        gate; counted as risk, it kept its Book's validation flag up for the
        Book's life. The flag records the declaration on this explanation axis
        and leaves the validity axis truthful.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Fine-grained state flags for a spell index. Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """
    # Topology / graph-level
    new_index = "new_index"             # first time we see this index
    structure_changed = "structure_changed"       # profile / wiring changed
    dependencies_changed = "dependencies_changed"    # direct deps set changed
    impacted_by_dependency = "impacted_by_dependency"  # downstream of something that changed

    # Contracts / sockets / mutation
    contract_unvalidated = "contract_unvalidated"    # has SpellContracts; needs a pass
    contract_violation = "contract_violation"      # contract failed; usually -> invalid
    mutation_candidate = "mutation_candidate"      # current version comes from MutationLab
    mutation_quarantined = "mutation_quarantined"    # candidate exists but not allowed in prod
    mutation_failed = "mutation_failed"         # last mutation release failed

    # Ops / incidents / policy
    has_open_incident = "has_open_incident"       # critical/blocking incident open
    anchored_component = "anchored_component"      # infra / non-mutable component
    config_missing = "config_missing"          # required config not present
    transfer_in_progress = "transfer_in_progress"    # ownership transfer is actively blocking resolution

    # Capability (registration)
    non_resolvable = "non_resolvable"          # selected version bound resolvable=False; owes no resolution verdict

    @classmethod
    def _missing_(cls, value: object) -> Optional[SpellState]:
        """
        Resolve a historical numeric flag to its original member.

        Current names use ordinary enum lookup. Values equal to the old
        integers remain readable; unknown or unhashable inputs return None
        so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, SpellState] = {
            1: cls.new_index,
            2: cls.structure_changed,
            3: cls.dependencies_changed,
            4: cls.impacted_by_dependency,
            5: cls.contract_unvalidated,
            6: cls.contract_violation,
            7: cls.mutation_candidate,
            8: cls.mutation_quarantined,
            9: cls.mutation_failed,
            10: cls.has_open_incident,
            11: cls.anchored_component,
            12: cls.config_missing,
            13: cls.transfer_in_progress,
            14: cls.non_resolvable,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None
