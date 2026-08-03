"""
Unit tests for the plane's participation model - the COMMIT half.

WHY THIS FILE EXISTS SEPARATELY FROM THE STRATEGY TESTS: configure, enable and
disable claim IDENTICALLY. Tested on claims alone the three look
interchangeable, and the obvious conclusion - collapse them into one family - is
wrong. What separates them is the participation state each writes at commit, and
that is what this file asserts.

It also pins the property the whole model exists for: EXACTLY ONE STATE EMITS.
A subsystem that is registered, configured, disabled or unknown is silent, and
those are four different silences rather than one.

Run:
    pytest tests/unit/melder/aether/aetheric_mediator -q
"""

import time

import pytest

from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.information_registry import (
    InformationRegistry,
)
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.participation import (
    ParticipationConditions,
    ParticipationState,
)
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.strategies.subsystem_configure_transaction_strategy import (
    SubsystemConfigureTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_disable_transaction_strategy import (
    SubsystemDisableTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_enable_transaction_strategy import (
    SubsystemEnableTransactionStrategy,
)
from melder.aether.aetheric_mediator.transaction_type import TransactionType

SUBSYSTEM = "crystallizer"


@pytest.fixture(name="registry")
def _registry():
    """One real registry per test, torn down after."""
    built = InformationRegistry()
    try:
        yield built
    finally:
        built.cleanup()


@pytest.fixture(name="submitter")
def _submitter():
    """One real claimant. Commit deltas take an `Identity`, so tests supply one."""
    built = Identity(kind="crystallizer", identity_id="activator")
    try:
        yield built
    finally:
        built.cleanup()


def _staged(transaction_type, subsystem_name=SUBSYSTEM, **conditions):
    """
    Build one real `StagedTransaction` for a subsystem edge.

    Constructing the genuine record rather than a stand-in matters here: the
    commit deltas read `metadata` and `request_id` off it, and a stub would let
    a delta pass while relying on a shape the real record does not have.
    """
    metadata = {"subsystem_name": subsystem_name}
    metadata.update(conditions)
    return StagedTransaction(
        request_id="req-{0}-{1}".format(transaction_type.value, subsystem_name),
        transaction_type=transaction_type,
        submitter_kind="subsystem",
        submitter_id=subsystem_name,
        admitted_at=time.time(),
        granted_scopes=(ScopeKey.world(), ScopeKey.subsystem(subsystem_name)),
        metadata=metadata,
    )


def _commit(family, registry, submitter, staged):
    """Run one family's commit delta and clean the record it was given."""
    try:
        family.apply_commit_delta(
            information_registry=registry, submitter=submitter, staged=staged
        )
    finally:
        staged.cleanup()


# --------------------------------------------------------------------------
# The vocabulary
# --------------------------------------------------------------------------

def test_exactly_one_state_emits():
    """
    The whole model rests on this. If a second member ever starts emitting,
    every gate written against `emits` silently widens, and the subsystem that
    was supposed to be quiet starts being asked for work.
    """
    emitting = tuple(
        member for member in ParticipationState if member.emits
    )
    assert emitting == (ParticipationState.ENABLED,)


def test_every_state_is_reachable_by_an_edge(registry, submitter):
    """
    A state no edge can write is a dead branch every reader carries forever.
    Each member here is produced by the verb or family that owns it.
    """
    registry.announce_participant("a")
    _commit(
        SubsystemConfigureTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_CONFIGURE, "b"),
    )
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE, "c"),
    )
    _commit(
        SubsystemDisableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_DISABLE, "d"),
    )
    reached = {
        registry.participation_state(name) for name in ("a", "b", "c", "d")
    }
    assert reached == set(ParticipationState)


def test_undeclared_keys_are_dropped_not_stored():
    """
    Metadata is caller-controlled. Without a declared key set a subsystem could
    widen its own registry row with anything it liked, and every reader would
    then have to defend against a store with no shape.
    """
    selected = ParticipationConditions.select(
        {"worker_count": 4, "subsystem_name": "x", "smuggled": "nope"}
    )
    assert selected == {"worker_count": 4}


# --------------------------------------------------------------------------
# The three families differ by what they WRITE, not by what they claim
# --------------------------------------------------------------------------

def test_the_three_lifecycle_families_write_three_different_states(
        registry, submitter
):
    """
    THE REASON THE THREE FAMILIES ARE NOT ONE. Their claim sets are equal - the
    strategy tests assert that - so this is the only place the split is
    justified. Collapsing them would mean passing the target state through
    caller-controlled metadata instead of the closed vocabulary.
    """
    written = []
    for family, transaction_type in (
        (SubsystemConfigureTransactionStrategy,
         TransactionType.SUBSYSTEM_CONFIGURE),
        (SubsystemEnableTransactionStrategy,
         TransactionType.SUBSYSTEM_ENABLE),
        (SubsystemDisableTransactionStrategy,
         TransactionType.SUBSYSTEM_DISABLE),
    ):
        _commit(family, registry, submitter, _staged(transaction_type))
        written.append(registry.participation_state(SUBSYSTEM))

    assert written == [
        ParticipationState.CONFIGURED,
        ParticipationState.ENABLED,
        ParticipationState.DISABLED,
    ]


def test_enabling_is_the_only_edge_that_makes_a_subsystem_emit(
        registry, submitter
):
    """Owner constraint 6, asserted rather than described."""
    _commit(
        SubsystemConfigureTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_CONFIGURE, worker_count=4),
    )
    assert registry.is_participating(SUBSYSTEM) is False

    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE),
    )
    assert registry.is_participating(SUBSYSTEM) is True

    _commit(
        SubsystemDisableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_DISABLE),
    )
    assert registry.is_participating(SUBSYSTEM) is False


def test_enabling_without_conditions_keeps_the_configured_ones(
        registry, submitter
):
    """
    THE NORMAL SEQUENCE IS CONFIGURE THEN ENABLE. If the enable passed an empty
    mapping rather than None, the settings would be erased at the exact moment
    the subsystem started running with them.
    """
    _commit(
        SubsystemConfigureTransactionStrategy, registry, submitter,
        _staged(
            TransactionType.SUBSYSTEM_CONFIGURE,
            worker_count=4,
            parallel_enabled=True,
        ),
    )
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE),
    )
    assert registry.participant_conditions(SUBSYSTEM) == {
        "parallel_enabled": True, "worker_count": 4,
    }


def test_reconfiguring_a_running_subsystem_does_not_switch_it_off(
        registry, submitter
):
    """
    Writing CONFIGURED over ENABLED would claim the subsystem stopped, which it
    did not. The rule lives in `record_conditions` so there is one place to be
    right about it, and it is safe only because the family holds the subsystem
    exclusively while it reads and writes.
    """
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE, worker_count=4),
    )
    _commit(
        SubsystemConfigureTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_CONFIGURE, worker_count=8),
    )
    assert registry.participation_state(SUBSYSTEM) is ParticipationState.ENABLED
    assert registry.participant_conditions(SUBSYSTEM) == {"worker_count": 8}


def test_disabling_keeps_the_conditions_it_was_running_with(
        registry, submitter
):
    """
    "What was it running with when it stopped" is the first question asked after
    a subsystem goes quiet. Retaining the conditions is safe ONLY because the
    state guards them - `is_participating` already reads False - so nothing can
    mistake them for live settings.
    """
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE, policy_version="v2"),
    )
    _commit(
        SubsystemDisableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_DISABLE),
    )
    assert registry.participant_conditions(SUBSYSTEM) == {"policy_version": "v2"}
    assert registry.is_participating(SUBSYSTEM) is False


def test_a_commit_delta_still_stamps_the_fact_baseline(registry, submitter):
    """
    Overriding the delta must EXTEND the base behaviour, not replace it. A
    family that forgot its `super()` call would leave reporting claiming
    freshness it never stamped.
    """
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE),
    )
    baseline = registry.get_fact(ScopeKey.subsystem(SUBSYSTEM))
    assert baseline is not None
    assert baseline["fact_family"] == TransactionType.SUBSYSTEM_ENABLE.value


def test_an_unnameable_subject_records_nothing(registry, submitter):
    """
    A lifecycle transaction with no subject took `world` EXCLUSIVE and is a
    caller error, but refusing it is admission's job. The delta must leave the
    store empty rather than inventing a row for a subsystem it cannot name.
    """
    staged = StagedTransaction(
        request_id="req-nameless",
        transaction_type=TransactionType.SUBSYSTEM_ENABLE,
        submitter_kind="subsystem",
        submitter_id="unknown",
        admitted_at=time.time(),
        granted_scopes=(ScopeKey.world(),),
        metadata={"worker_count": 4},
    )
    _commit(SubsystemEnableTransactionStrategy, registry, submitter, staged)
    assert registry.known_subsystems() == ()


# --------------------------------------------------------------------------
# Absence, registration, and the difference between them
# --------------------------------------------------------------------------

def test_unknown_and_disabled_are_different_answers(registry, submitter):
    """
    THE FAILURE THIS MODEL EXISTS TO SEPARATE. A subsystem nobody wired in and
    one that was switched off on purpose both do nothing, and they need
    completely different fixes. A store that recorded presence alone gave the
    same answer for both.
    """
    assert registry.participation_state("never-seen") is None

    _commit(
        SubsystemDisableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_DISABLE),
    )
    assert (
        registry.participation_state(SUBSYSTEM) is ParticipationState.DISABLED
    )


def test_announcing_is_not_enabling(registry):
    """
    A roster arrival says a subsystem exists, not that it is running. Landing
    it anywhere but REGISTERED would start emitting for something that has not
    started.
    """
    assert registry.announce_participant(SUBSYSTEM) is True
    assert (
        registry.participation_state(SUBSYSTEM) is ParticipationState.REGISTERED
    )
    assert registry.is_participating(SUBSYSTEM) is False


def test_re_announcing_never_demotes_a_running_subsystem(registry, submitter):
    """
    A subsystem that re-announces while ENABLED must stay ENABLED. Knocking it
    back to REGISTERED would silence something that is still running, which is
    the worst direction for this bug to go.
    """
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE, worker_count=4),
    )
    assert registry.announce_participant(SUBSYSTEM) is False
    assert registry.participation_state(SUBSYSTEM) is ParticipationState.ENABLED
    assert registry.participant_conditions(SUBSYSTEM) == {"worker_count": 4}


def test_forgetting_removes_the_row_where_disabling_keeps_it(
        registry, submitter
):
    """
    The two verbs are not interchangeable and the store must show it: disable
    is a lifecycle transition, forget is teardown.
    """
    _commit(
        SubsystemDisableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_DISABLE),
    )
    assert registry.known_subsystems() == (SUBSYSTEM,)

    assert registry.forget_participant(SUBSYSTEM) is True
    assert registry.known_subsystems() == ()
    assert registry.participation_state(SUBSYSTEM) is None
    assert registry.forget_participant(SUBSYSTEM) is False


# --------------------------------------------------------------------------
# Reporting - detached, and honest about who is silent
# --------------------------------------------------------------------------

def test_the_roster_reports_every_state_not_only_the_emitting_ones(
        registry, submitter
):
    """
    A roster that hid its silent members would be useless for the question it
    is usually asked to settle, which is why nothing is happening.
    """
    registry.announce_participant("mutation_research")
    _commit(
        SubsystemConfigureTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_CONFIGURE, "nexus"),
    )
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE),
    )

    assert registry.known_subsystems() == (
        SUBSYSTEM, "mutation_research", "nexus",
    )
    assert registry.participants_in_state(ParticipationState.ENABLED) == (
        SUBSYSTEM,
    )
    assert registry.participants_in_state(ParticipationState.REGISTERED) == (
        "mutation_research",
    )
    assert registry.participants_in_state(ParticipationState.CONFIGURED) == (
        "nexus",
    )


def test_reported_rows_are_detached_from_the_store(registry, submitter):
    """
    Every read here returns values. A caller that could mutate the return would
    be able to rewrite what the plane believes about a subsystem without a
    transaction, which defeats the point of gating the writes.
    """
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE, worker_count=4),
    )
    rows = registry.describe_participants()
    rows[0]["conditions"]["worker_count"] = 999
    registry.participant_conditions(SUBSYSTEM)["worker_count"] = 999

    assert registry.participant_conditions(SUBSYSTEM) == {"worker_count": 4}


def test_the_snapshot_separates_who_exists_from_who_is_emitting(
        registry, submitter
):
    """
    `participant_count` is the roster; `emitting_count` is the number an
    operator actually wants. Reporting only the first reads as three live
    subsystems when one is running.
    """
    registry.announce_participant("mutation_research")
    registry.announce_participant("nexus")
    _commit(
        SubsystemEnableTransactionStrategy, registry, submitter,
        _staged(TransactionType.SUBSYSTEM_ENABLE),
    )
    snapshot = registry.describe()

    assert snapshot["participant_count"] == 3
    assert snapshot["emitting_count"] == 1
    assert [row["emits"] for row in snapshot["participants"]] == [
        True, False, False,
    ]


# --------------------------------------------------------------------------
# Error paths and lifecycle
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad_name", ["", "   ", None, 42])
def test_an_unnameable_subsystem_is_refused(registry, bad_name):
    """
    A blank name matches no `ScopeKey.subsystem(...)` key. Accepting one
    produces a row nothing can ever claim against, which reads as "the
    subsystem is live" while being unreachable.
    """
    with pytest.raises(ValueError):
        registry.announce_participant(bad_name)


def test_a_state_outside_the_vocabulary_is_refused(registry):
    """
    The vocabulary is closed. Accepting the bare string `"enabled"` would let a
    caller write a value `emits` cannot be asked of, and the gate would raise
    on read instead of on write.
    """
    with pytest.raises(TypeError):
        registry.set_participation(
            subsystem_name=SUBSYSTEM, state="enabled", reporter="req-1"
        )


def test_a_live_object_cannot_be_stored_as_a_condition(registry):
    """
    The plane must hold no reference it could keep alive. A live object here
    would defeat `describe()` and pin the subsystem it describes.
    """
    with pytest.raises(TypeError):
        registry.set_participation(
            subsystem_name=SUBSYSTEM,
            state=ParticipationState.ENABLED,
            reporter="req-1",
            conditions={"worker_count": object()},
        )


def test_an_unattributed_state_change_is_refused(registry):
    """
    Every state change names the transaction that made it. A row that cannot
    say who moved it is not evidence.
    """
    with pytest.raises(ValueError):
        registry.set_participation(
            subsystem_name=SUBSYSTEM,
            state=ParticipationState.ENABLED,
            reporter="",
        )


def test_participant_verbs_refuse_after_cleanup():
    """Every participant verb is guarded, like the rest of the plane surface."""
    registry = InformationRegistry()
    registry.announce_participant(SUBSYSTEM)
    registry.cleanup()
    for call in (
        lambda: registry.announce_participant(SUBSYSTEM),
        lambda: registry.forget_participant(SUBSYSTEM),
        lambda: registry.participation_state(SUBSYSTEM),
        lambda: registry.is_participating(SUBSYSTEM),
        lambda: registry.participant_conditions(SUBSYSTEM),
        lambda: registry.known_subsystems(),
        lambda: registry.describe_participants(),
        lambda: registry.participants_in_state(ParticipationState.ENABLED),
    ):
        with pytest.raises(RuntimeError):
            call()


# --------------------------------------------------------------------------
# One store, not two
# --------------------------------------------------------------------------

def test_the_roster_and_the_participation_states_are_one_store():
    """
    THE DUPLICATION THIS REPLACED. `Mediator` kept its own participant map
    while the strategies wrote to the registry, so the roster could say a
    subsystem was live while the registry had never heard of it. Announcing
    through the plane must be visible through reporting, and vice versa.
    """
    plane = Mediator(max_wait_seconds=0.1)
    try:
        plane.register_participant(SUBSYSTEM)
        assert (
            plane.reporting.participation_state(SUBSYSTEM)
            is ParticipationState.REGISTERED
        )
        assert plane.has_participant(SUBSYSTEM) is True
        assert plane.is_participating(SUBSYSTEM) is False

        plane.reporting.set_participation(
            subsystem_name=SUBSYSTEM,
            state=ParticipationState.ENABLED,
            reporter="req-1",
        )
        assert plane.is_participating(SUBSYSTEM) is True
        assert plane.participants_in_state(ParticipationState.ENABLED) == (
            SUBSYSTEM,
        )
    finally:
        plane.cleanup()


def test_the_plane_roster_lists_subsystems_that_are_not_running():
    """
    `participants()` is the roster, not the emission set. A caller gating work
    on it would run against subsystems that are configured but never started.
    """
    plane = Mediator(max_wait_seconds=0.1)
    try:
        plane.register_participant("nexus")
        plane.register_participant(SUBSYSTEM)
        plane.reporting.set_participation(
            subsystem_name="nexus",
            state=ParticipationState.ENABLED,
            reporter="req-1",
        )
        assert plane.participants() == (SUBSYSTEM, "nexus")
        assert plane.describe()["participants"] == (SUBSYSTEM, "nexus")
        assert tuple(
            name for name in plane.participants()
            if plane.is_participating(name)
        ) == ("nexus",)
    finally:
        plane.cleanup()
