from enum import StrEnum
from typing import Optional

class SpellStateChangeReason(StrEnum):
    """
    Last event that *changed* the state of an index.

    Values exactly match member names. Historical numeric values 1-27 remain
    readable by value, including in older enum pickle payloads.

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
        `mutation_contract_set` / `mutation_contract_cleared`.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Last event that *changed* the state of an index. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """
    # Registrations / bindings
    new_index = "new_index"            # first time this index was registered
    register_or_rebind = "register_or_rebind"     # new Spell bound to existing index

    # Structure / dependency graph
    structure_changed = "structure_changed"      # constructor / DI shape / profile changed
    dependencies_changed = "dependencies_changed"   # direct dependency set changed
    dependency_changed = "dependency_changed"     # one of our deps changed (impact event)
    impacted_by_dependency = "impacted_by_dependency" # we were marked dirty due to dep changes

    # Contracts
    contract_unvalidated = "contract_unvalidated"   # SpellContracts added / changed; needs pass
    contract_violation = "contract_violation"     # contract check failed

    # Mutations (version graph)
    mutation_promoted = "mutation_promoted"      # new version promoted to SpellIndex.selected_spell_id
    mutation_rolled_back = "mutation_rolled_back"   # reverted to a previous version

    # Selection (general, not a mutation)
    selected_different_spell = "selected_different_spell"  # notch repointed the index to a different existing member

    # Mutations (override overlay; the *_contract_* names are historical)
    mutation_contract_set = "mutation_contract_set"      # overlay set
    mutation_contract_cleared = "mutation_contract_cleared"  # overlay removed / back to normal
    mutation_failed = "mutation_failed"            # last mutation run/validation failed
    mutation_candidate = "mutation_candidate"         # index now backed by a candidate build
    mutation_quarantined = "mutation_quarantined"       # candidate or index quarantined

    # Validation
    validation_passed = "validation_passed"       # latest validation cycle succeeded
    validation_failed = "validation_failed"       # validation surfaced errors / gating

    # Ops / incidents / config
    incident_opened = "incident_opened"        # critical incident opened for this index
    incident_resolved = "incident_resolved"      # last known incident resolved
    config_missing = "config_missing"         # required config missing / invalid
    config_supplied = "config_supplied"        # config fixed / supplied
    anchored_component = "anchored_component"     # marked non-mutable infra component
    transfer_in_progress = "transfer_in_progress"   # ownership transfer gate

    # Disposal
    cleaned_up_spell = "cleaned_up_spell"       # owning spell disposed via cleanup_spell

    # Manual / catch-all
    explicit_mark = "explicit_mark"          # explicitly marked dirty/attention-needed
    other = "other"                  # anything else; explain in Incident/details

    @classmethod
    def _missing_(cls, value: object) -> Optional[SpellStateChangeReason]:
        """
        Resolve a historical numeric change reason to its original member.

        Current names use ordinary enum lookup. Values equal to the old
        integers remain readable; unknown or unhashable inputs return None
        so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, SpellStateChangeReason] = {
            1: cls.new_index,
            2: cls.register_or_rebind,
            3: cls.structure_changed,
            4: cls.dependencies_changed,
            5: cls.dependency_changed,
            6: cls.impacted_by_dependency,
            7: cls.contract_unvalidated,
            8: cls.contract_violation,
            9: cls.mutation_promoted,
            10: cls.mutation_rolled_back,
            11: cls.selected_different_spell,
            12: cls.mutation_contract_set,
            13: cls.mutation_contract_cleared,
            14: cls.mutation_failed,
            15: cls.mutation_candidate,
            16: cls.mutation_quarantined,
            17: cls.validation_passed,
            18: cls.validation_failed,
            19: cls.incident_opened,
            20: cls.incident_resolved,
            21: cls.config_missing,
            22: cls.config_supplied,
            23: cls.anchored_component,
            24: cls.transfer_in_progress,
            25: cls.cleaned_up_spell,
            26: cls.explicit_mark,
            27: cls.other,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None
