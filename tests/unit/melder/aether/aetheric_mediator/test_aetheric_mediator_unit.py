"""
Unit tests for the aetheric mediator plane - isolated contracts.

WHY THIS FILE MATTERS: every harness run against this package so far executed on
a Python 3.10 sandbox with `StrEnum` and `Cleanable` SUBSTITUTED, because the
sandbox cannot obtain a 3.14t interpreter. That proved the algorithm and nothing
about the shipped wiring. These tests run against the REAL `Cleanable` and the
REAL `StrEnum` on the repo's own interpreter, which is the gap they close.

Run:
    pytest tests/unit/melder/aether/aetheric_mediator -q
"""

import threading

import pytest

from melder.aether.aetheric_mediator.admission_orchestrator import (
    AdmissionOrchestrator,
)
from melder.aether.aetheric_mediator.admission_result import (
    AdmissionReason,
    AdmissionResult,
)
from melder.aether.aetheric_mediator.claim_mode import ClaimCompatibility, ClaimMode
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.information_registry import InformationRegistry
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.strategy_builder import StrategyBuilder
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.aether.aetheric_mediator.transaction_session import (
    OutcomePolicy,
    SessionStatus,
    TransactionSession,
)
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy
from melder.aether.aetheric_mediator.transaction_type import TransactionType


def _identity(kind: str = "crystallizer", identity_id: str = "loader") -> Identity:
    """Build one test identity."""
    return Identity(kind=kind, identity_id=identity_id)


def _request(
        request_id: str = "R1",
        claims=None,
        submitter: Identity = None,
) -> TransactionRequest:
    """Build one frozen request with test defaults."""
    return TransactionRequest.build(
        request_id=request_id,
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=submitter if submitter is not None else _identity(),
        scope_claims=claims or {ScopeKey.frame("A"): ClaimMode.EXCLUSIVE},
        metadata={},
    )


def _session(
        outcome_policy: OutcomePolicy = OutcomePolicy.UNWIND,
        request: TransactionRequest = None,
) -> TransactionSession:
    """
    Build one session with its staged record.

    The staged record is built ONCE at admission in production and carried on
    the session; tests must mirror that so `admitted_at` semantics match.
    """
    built = request if request is not None else _request()
    return TransactionSession(
        request=built,
        staged=StagedTransaction.from_request(request=built, admitted_at=0.0),
        holder=_identity(),
        outcome_policy=outcome_policy,
    )


# --------------------------------------------------------------------------
# Claim vocabulary
# --------------------------------------------------------------------------

def test_matrix_matches_devops_semantics_exactly():
    """A mode coexists only with itself; EXCLUSIVE not even with that."""
    assert ClaimCompatibility.permits(ClaimMode.SHARED, ClaimMode.SHARED)
    assert ClaimCompatibility.permits(ClaimMode.INTENT, ClaimMode.INTENT)
    assert not ClaimCompatibility.permits(ClaimMode.SHARED, ClaimMode.INTENT)
    assert not ClaimCompatibility.permits(ClaimMode.INTENT, ClaimMode.SHARED)
    for mode in ClaimMode:
        assert not ClaimCompatibility.permits(ClaimMode.EXCLUSIVE, mode)
        assert not ClaimCompatibility.permits(mode, ClaimMode.EXCLUSIVE)


def test_claim_mode_survives_string_apis():
    """StrEnum members travel into payloads and logs as plain strings."""
    assert ClaimMode.EXCLUSIVE == "x"
    assert ClaimMode("ix") is ClaimMode.INTENT
    assert "mode={0}".format(ClaimMode.SHARED.value) == "mode=s"


def test_compatibility_rejects_non_modes():
    """A stray string must not be silently treated as a mode."""
    with pytest.raises(TypeError):
        ClaimCompatibility.permits("x", ClaimMode.SHARED)


# --------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------

def test_identity_equality_ignores_label_and_thread():
    """Equality is (kind, id) only, so a reconstructed identity matches."""
    first = Identity(kind="k", identity_id="1", label="a", thread_ident=11)
    second = Identity(kind="k", identity_id="1", label="b", thread_ident=22)
    assert first == second
    assert hash(first) == hash(second)
    assert first != Identity(kind="k", identity_id="2")


def test_identity_rejects_unnameable_claimants():
    """A blank id would make unrelated claimants compare equal."""
    with pytest.raises(ValueError):
        Identity(kind="", identity_id="1")
    with pytest.raises(ValueError):
        Identity(kind="k", identity_id="   ")


# --------------------------------------------------------------------------
# Scope keys
# --------------------------------------------------------------------------

def test_scope_keys_reject_empty_names():
    """An empty key would collide with every other empty-named claim."""
    with pytest.raises(ValueError):
        ScopeKey.frame("")
    with pytest.raises(ValueError):
        ScopeKey.subsystem("  ")
    assert ScopeKey.is_world(ScopeKey.world())
    assert ScopeKey.frame("A") != ScopeKey.subsystem("A")


# --------------------------------------------------------------------------
# Claim table
# --------------------------------------------------------------------------

def test_acquisition_is_all_or_nothing():
    """A partly-grantable request must take NOTHING."""
    table = ClaimTable()
    try:
        held, other = _identity("a", "1"), _identity("b", "2")
        assert table.try_acquire(held, {"s1": ClaimMode.EXCLUSIVE}) == ()
        blocks = table.try_acquire(
            other, {"s1": ClaimMode.EXCLUSIVE, "s2": ClaimMode.EXCLUSIVE}
        )
        assert blocks
        assert table.held_scopes(other) == (), "free scope must not be taken"
    finally:
        table.cleanup()


def test_refusal_carries_named_blocking_evidence():
    """Refusal names scope, holder, and modes - not a bare False."""
    table = ClaimTable()
    try:
        table.try_acquire(_identity("crystallizer", "loader"), {"s1": ClaimMode.EXCLUSIVE})
        blocks = table.try_acquire(_identity("agent", "7"), {"s1": ClaimMode.SHARED})
        assert len(blocks) == 1
        rendered = blocks[0].describe()
        assert "s1" in rendered and "crystallizer" in rendered
    finally:
        table.cleanup()


def test_reentry_is_a_noop_and_never_an_upgrade():
    """A holder never blocks itself and never silently strengthens its mode."""
    table = ClaimTable()
    try:
        who = _identity()
        assert table.try_acquire(who, {"s1": ClaimMode.SHARED}) == ()
        assert table.try_acquire(who, {"s1": ClaimMode.EXCLUSIVE}) == ()
        granted = table.describe()["scopes"]["s1"]
        assert granted[0][1] == ClaimMode.SHARED.value
    finally:
        table.cleanup()


def test_release_is_idempotent_and_frees_the_scope():
    """A finally-block may release unconditionally."""
    table = ClaimTable()
    try:
        who = _identity()
        table.try_acquire(who, {"s1": ClaimMode.EXCLUSIVE})
        assert table.release_holder(who) == 1
        assert table.release_holder(who) == 0
        assert table.try_acquire(_identity("b", "2"), {"s1": ClaimMode.EXCLUSIVE}) == ()
    finally:
        table.cleanup()


def test_exclusive_contention_never_overlaps_under_threads():
    """The core mutual-exclusion guarantee, exercised concurrently."""
    table = ClaimTable()
    overlap, live, guard = [], [], threading.Lock()

    def worker(index: int) -> None:
        me = Identity(kind="w", identity_id=str(index))
        try:
            table.acquire(me, {"hot": ClaimMode.EXCLUSIVE}, timeout_seconds=15.0)
        except RuntimeError:
            return
        with guard:
            live.append(index)
            if len(live) > 1:
                overlap.append(tuple(live))
        with guard:
            live.remove(index)
        table.release_holder(me)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    try:
        assert overlap == [], "two holders were live on one exclusive scope"
        assert table.describe()["scope_count"] == 0
    finally:
        table.cleanup()


def test_shared_holders_coexist_concurrently():
    """SHARED must genuinely admit in parallel, not merely be documented so."""
    table = ClaimTable()
    try:
        holders = [Identity(kind="r", identity_id=str(i)) for i in range(8)]
        for holder in holders:
            assert table.try_acquire(holder, {"s1": ClaimMode.SHARED}) == ()
        assert len(table.describe()["scopes"]["s1"]) == 8
    finally:
        table.cleanup()


def test_cleanup_wakes_parked_waiters():
    """A cleaned table must never strand a waiting thread."""
    table = ClaimTable()
    table.try_acquire(_identity("a", "1"), {"s1": ClaimMode.EXCLUSIVE})
    outcome = []

    def waiter() -> None:
        try:
            table.acquire(
                _identity("b", "2"), {"s1": ClaimMode.EXCLUSIVE}, timeout_seconds=15.0
            )
            outcome.append("acquired")
        except RuntimeError:
            outcome.append("raised")

    thread = threading.Thread(target=waiter)
    thread.start()
    table.cleanup()
    thread.join(timeout=10.0)
    assert not thread.is_alive(), "waiter stranded on a cleaned table"
    assert outcome == ["raised"]


def test_acquire_times_out_with_blocking_evidence():
    """A timeout must name what blocked it."""
    table = ClaimTable()
    try:
        table.try_acquire(_identity("a", "1"), {"s1": ClaimMode.EXCLUSIVE})
        with pytest.raises(RuntimeError) as excinfo:
            table.acquire(
                _identity("b", "2"), {"s1": ClaimMode.EXCLUSIVE}, timeout_seconds=0.05
            )
        assert "s1" in str(excinfo.value)
    finally:
        table.cleanup()


# --------------------------------------------------------------------------
# Request and verdict
# --------------------------------------------------------------------------

def test_request_requires_explicit_complete_claims():
    """No implicit defaulting - an empty claim set isolates nothing."""
    with pytest.raises(ValueError):
        TransactionRequest.build(
            request_id="R",
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_identity(),
            scope_claims={},
            metadata={},
        )


def test_request_rejects_non_mode_claim_values():
    """A raw string mode must not slip into the claim set."""
    with pytest.raises(TypeError):
        TransactionRequest.build(
            request_id="R",
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_identity(),
            scope_claims={"s1": "x"},
            metadata={},
        )


def test_request_is_frozen_and_normalised():
    """Frozen before admission; sorted so evidence renders stably."""
    request = _request(claims={"z": ClaimMode.SHARED, "a": ClaimMode.EXCLUSIVE})
    assert request.scope_keys() == ("a", "z")
    assert request.claim_map()["a"] is ClaimMode.EXCLUSIVE
    with pytest.raises(Exception):
        request.request_id = "mutated"


def test_request_copies_metadata_defensively():
    """A later caller mutation must not alter a frozen request."""
    metadata = {"frame": "A"}
    request = TransactionRequest.build(
        request_id="R",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={"s1": ClaimMode.EXCLUSIVE},
        metadata=metadata,
    )
    metadata["frame"] = "MUTATED"
    assert request.metadata["frame"] == "A"


def test_refusal_without_a_reason_is_illegal():
    """A silent refusal is the failure this type exists to prevent."""
    with pytest.raises(ValueError):
        AdmissionResult.refused(reasons=())
    assert AdmissionResult.granted().admitted
    assert AdmissionResult.granted().describe() == "admitted"


# --------------------------------------------------------------------------
# Dataclass value-only discipline (synaptic AGENTS.MD 5.15 / banned_patterns)
# --------------------------------------------------------------------------

def test_metadata_rejects_live_object_references():
    """
    A frozen record must not be able to smuggle a live object.

    `metadata` is annotated with `Any` values because the permitted domain is
    recursive, and `Any` would otherwise permit exactly the thing the
    value-only dataclass rule forbids - a live `Conduit` or `Spellbook` inside
    a record this class promises is detached and loggable.
    """

    class _Live:
        pass

    with pytest.raises(TypeError, match="VALUE-ONLY"):
        TransactionRequest.build(
            request_id="R",
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_identity(),
            scope_claims={"s1": ClaimMode.EXCLUSIVE},
            metadata={"conduit": _Live()},
        )


def test_metadata_rejects_objects_nested_in_containers():
    """The guard must recurse, not just check the top level."""

    class _Live:
        pass

    with pytest.raises(TypeError, match="VALUE-ONLY"):
        TransactionRequest.build(
            request_id="R",
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_identity(),
            scope_claims={"s1": ClaimMode.EXCLUSIVE},
            metadata={"nested": {"deeper": [1, 2, _Live()]}},
        )


def test_metadata_rejects_non_string_keys():
    """Non-string keys do not survive a JSON round trip."""
    with pytest.raises(TypeError):
        TransactionRequest.build(
            request_id="R",
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_identity(),
            scope_claims={"s1": ClaimMode.EXCLUSIVE},
            metadata={7: "seven"},
        )


def test_metadata_accepts_nested_value_containers():
    """Values and containers of values are legitimate and must pass."""
    request = TransactionRequest.build(
        request_id="R",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={"s1": ClaimMode.EXCLUSIVE},
        metadata={
            "frame": "A",
            "count": 3,
            "ratio": 0.5,
            "flag": True,
            "absent": None,
            "ids": ["a", "b"],
            "nested": {"deep": [1, "two", None]},
        },
    )
    # Sequences are normalised to tuples, so the record is frozen at depth
    # rather than merely copied at the top.
    assert request.metadata["nested"]["deep"] == (1, "two", None)
    assert request.metadata["ids"] == ("a", "b")


def test_metadata_is_deep_copied_not_shallow():
    """
    A shallow copy would leave nested containers shared with the caller.

    `dict(metadata)` alone copies only the top level, so a caller mutating a
    nested list would still be mutating a frozen record.
    """
    nested = ["a"]
    request = TransactionRequest.build(
        request_id="R",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={"s1": ClaimMode.EXCLUSIVE},
        metadata={"ids": nested},
    )
    nested.append("MUTATED")
    assert request.metadata["ids"] == ("a",)


def test_staged_transaction_shares_its_requests_frozen_metadata():
    """
    The two records SHARE one structure, which is safe only because it is
    frozen.

    This inverts an earlier rule. While metadata was a plain `Dict`, the two
    records had to hold separate copies or a mutation through one would show up
    in the other. Now that `MetadataPolicy` returns a deeply frozen structure
    there is nothing to defend against, so copying would only add an allocation
    per transaction and a second object for the finishing thread to release.
    """
    from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction

    request = TransactionRequest.build(
        request_id="R",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={"s1": ClaimMode.EXCLUSIVE},
        metadata={"frame": "A"},
    )
    staged = StagedTransaction.from_request(request=request, admitted_at=0.0)
    assert staged.metadata is request.metadata
    with pytest.raises(TypeError):
        staged.metadata["frame"] = "MUTATED"
    assert request.metadata["frame"] == "A"


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------

def test_orchestrator_refusal_leaves_no_trace():
    """A refused request touches neither registry nor claim table."""
    table, orchestrator = ClaimTable(), AdmissionOrchestrator()
    try:
        first, second = _identity("a", "1"), _identity("b", "2")
        orchestrator.admit(
            request=_request("R1", submitter=first), holder=first, claim_table=table
        )
        verdict = orchestrator.admit(
            request=_request("R2", submitter=second), holder=second, claim_table=table
        )
        assert not verdict.admitted
        assert AdmissionReason.SCOPE_CONTENDED in verdict.reasons
        assert verdict.blocked_scopes == (ScopeKey.frame("A"),)
        assert orchestrator.get_in_flight("R2") is None
        assert table.held_scopes(second) == ()
    finally:
        orchestrator.cleanup()
        table.cleanup()


def test_orchestrator_rejects_mismatched_holder():
    """Evidence must never name a claimant other than the one claiming."""
    table, orchestrator = ClaimTable(), AdmissionOrchestrator()
    try:
        with pytest.raises(ValueError):
            orchestrator.admit(
                request=_request(submitter=_identity("a", "1")),
                holder=_identity("b", "2"),
                claim_table=table,
            )
    finally:
        orchestrator.cleanup()
        table.cleanup()


def test_orchestrator_release_is_idempotent():
    """Releasing an unknown request id is a safe no-op."""
    table, orchestrator = ClaimTable(), AdmissionOrchestrator()
    try:
        who = _identity()
        orchestrator.admit(
            request=_request("R1", submitter=who), holder=who, claim_table=table
        )
        assert orchestrator.release(
            request_id="R1", holder=who, claim_table=table
        ) is True
        assert orchestrator.release(
            request_id="R1", holder=who, claim_table=table
        ) is False
    finally:
        orchestrator.cleanup()
        table.cleanup()


# --------------------------------------------------------------------------
# Session and outcome policy
# --------------------------------------------------------------------------

def test_unwind_runs_inverses_newest_first():
    """Rollback order is reverse registration order."""
    order = []
    session = _session(OutcomePolicy.UNWIND)
    for name in ("first", "second", "third"):
        session.register_rollback_action(
            action=(lambda name=name: order.append(name)),
            description="undo {0}".format(name),
        )
    session.leave()
    status, failures = session.fail("boom")
    assert status is SessionStatus.ABORTED
    assert order == ["third", "second", "first"]
    assert failures == ()


def test_one_failing_inverse_does_not_stop_the_rest():
    """Best-effort per action; failures recorded, never dropped."""
    ran = []
    session = _session(OutcomePolicy.UNWIND)
    session.register_rollback_action(
        action=lambda: ran.append("a"), description="undo a"
    )

    def explode() -> None:
        raise ValueError("cleanup exploded")

    session.register_rollback_action(action=explode, description="undo b")
    session.register_rollback_action(
        action=lambda: ran.append("c"), description="undo c"
    )
    session.leave()
    _status, failures = session.fail("boom")
    assert ran == ["c", "a"]
    assert len(failures) == 1 and "undo b" in failures[0]
    assert session.describe()["unwind_failures"]


def test_leave_broken_runs_nothing_and_returns_residue():
    """The second outcome: keep the world, report what was left."""
    session = _session(OutcomePolicy.LEAVE_BROKEN)

    def must_not_run() -> None:
        raise AssertionError("LEAVE_BROKEN must not invoke inverses")

    session.register_rollback_action(
        action=must_not_run, description="tear down frame:C posture"
    )
    session.leave()
    status, residue = session.fail("stage 6 raised")
    assert status is SessionStatus.BROKEN
    assert residue == ("tear down frame:C posture",)


def test_broken_is_distinct_from_aborted():
    """Collapsing the two would erase whether repair work exists."""
    assert SessionStatus.BROKEN is not SessionStatus.ABORTED
    assert SessionStatus.BROKEN.value == "broken"


def test_rollback_action_requires_a_description():
    """An undescribed inverse is invisible residue under LEAVE_BROKEN."""
    session = _session()
    with pytest.raises(ValueError):
        session.register_rollback_action(action=lambda: None, description="  ")


def test_join_depth_and_double_fail_are_guarded():
    """Depth counts, and a terminal session cannot be failed twice."""
    session = _session()
    assert session.join() == 2
    assert session.leave() == 1
    assert session.leave() == 0
    session.fail("boom")
    with pytest.raises(RuntimeError):
        session.fail("again")


def test_commit_refuses_while_still_joined():
    """
    An inner scope must not terminate an outer one.

    Points at `mark_committing`, which is where the DEPTH guard now lives.
    It used to point at `mark_committed`, and that assertion would still pass
    after the commit pipeline was ported - but for the wrong reason: from OPEN,
    `mark_committed` now refuses on STATUS before depth is ever consulted. The
    depth rule would have kept a green test while losing its coverage.
    """
    session = _session()
    session.join()
    with pytest.raises(RuntimeError):
        session.mark_committing()


def test_committed_is_unreachable_without_passing_through_committing():
    """
    COMMITTED means "the commit pipeline ran", so it needs a path to say so.

    The old shape marked COMMITTED up front, which is why a transaction that
    died inside its own commit still reported success.
    """
    session = _session()
    session.leave()
    with pytest.raises(RuntimeError):
        session.mark_committed()
    session.mark_committing()
    assert session.status is SessionStatus.COMMITTING
    session.mark_committed()
    assert session.status is SessionStatus.COMMITTED


def test_foreign_thread_join_fails_fast_naming_the_owner():
    """A cross-thread re-begin is a caller bug, not a wait."""
    session = _session()
    captured = []

    def foreign() -> None:
        try:
            session.join()
        except RuntimeError as error:
            captured.append(str(error))

    thread = threading.Thread(target=foreign)
    thread.start()
    thread.join(timeout=10.0)
    assert captured and "owned by thread" in captured[0]


# --------------------------------------------------------------------------
# Strategy registry
# --------------------------------------------------------------------------

class _Noop(TransactionStrategy):
    """Minimal concrete strategy for registry tests."""

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {ScopeKey.world(): ClaimMode.INTENT}

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        return None

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        return None


def test_unregistered_type_raises_rather_than_defaulting():
    """A guessed claim set is how isolation is lost quietly."""
    builder = StrategyBuilder()
    try:
        with pytest.raises(KeyError):
            builder.resolve(TransactionType.AGENT_REPAIR)
    finally:
        builder.cleanup()


def test_registry_reports_gaps_and_rejects_instances():
    """Completeness is assertable at boot; instances are not classes."""
    builder = StrategyBuilder()
    try:
        builder.register(
            transaction_type=TransactionType.CHECKPOINT_LOAD, strategy=_Noop
        )
        assert builder.is_registered(TransactionType.CHECKPOINT_LOAD)
        assert TransactionType.CHECKPOINT_LOAD not in builder.missing_types()
        assert TransactionType.AGENT_REPAIR in builder.missing_types()
        with pytest.raises(TypeError):
            builder.register(
                transaction_type=TransactionType.AGENT_REPAIR, strategy=_Noop()
            )
    finally:
        builder.cleanup()


# --------------------------------------------------------------------------
# Lifecycle
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "factory",
    [ClaimTable, AdmissionOrchestrator, StrategyBuilder],
)
def test_cleanup_is_idempotent_and_use_after_clean_raises(factory):
    """Every owned component honours the Cleanable contract."""
    instance = factory()
    instance.cleanup()
    instance.cleanup()
    assert instance.cleaned is True
    with pytest.raises(RuntimeError):
        instance.describe()


@pytest.mark.parametrize(
    "factory",
    [ClaimTable, AdmissionOrchestrator, StrategyBuilder, InformationRegistry],
)
def test_concurrent_cleanup_does_not_double_free(factory):
    """
    REGRESSION: cleanup must re-check `_cleaned` INSIDE the lock.

    Sequential double-cleanup is caught by the test above, but it cannot
    catch the real race: two threads both pass the cheap outer
    `if self._cleaned` check, both enter the lock, both set the flag, and both
    fall through to the `del` statements - the loser raising AttributeError on
    an already-deleted slot. Free-threaded 3.14t removed the accidental
    serialisation that used to hide this, so it is a live hazard rather than a
    theoretical one.

    `cleanup_and_disposal.md` states the rule: check `_cleaned` before AND
    after locking.
    """
    instance = factory()
    barrier = threading.Barrier(8)
    failures = []

    def racer() -> None:
        barrier.wait()
        try:
            instance.cleanup()
        except BaseException as error:
            failures.append("{0}: {1}".format(type(error).__name__, error))

    threads = [threading.Thread(target=racer) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10.0)

    assert all(not thread.is_alive() for thread in threads)
    assert failures == [], "concurrent cleanup raised: {0}".format(failures)
    assert instance.cleaned is True


def test_concurrent_session_cleanup_does_not_double_free():
    """The same race on a session, which also clears two collections."""
    session = _session()
    barrier = threading.Barrier(8)
    failures = []

    def racer() -> None:
        barrier.wait()
        try:
            session.cleanup()
        except BaseException as error:
            failures.append("{0}: {1}".format(type(error).__name__, error))

    threads = [threading.Thread(target=racer) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10.0)

    assert all(not thread.is_alive() for thread in threads)
    assert failures == [], "concurrent cleanup raised: {0}".format(failures)
    assert session.cleaned is True


# --------------------------------------------------------------------------
# Metadata is a FROZEN value structure, not a dict behind a frozen dataclass
#
# `@dataclass(frozen=True)` blocks rebinding a field. It does nothing about
# mutating the object the field points at, so a `Dict` field leaves a record
# that advertises itself as detached and safe to retain while any holder can
# quietly edit it. These lock in the stronger property the records claim.
# --------------------------------------------------------------------------

def test_metadata_is_read_only_on_the_frozen_request():
    """The record advertises immutability; it must actually have it."""
    request = TransactionRequest.build(
        request_id="R1",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={ScopeKey.frame("A"): ClaimMode.EXCLUSIVE},
        metadata={"frame": "A"},
    )
    with pytest.raises(TypeError):
        request.metadata["frame"] = "B"
    with pytest.raises(TypeError):
        del request.metadata["frame"]


def test_metadata_is_frozen_all_the_way_down():
    """
    A shallow copy would still hand out mutable nested containers.

    Sequences come back as tuples and nested mappings as read-only views, so
    the record is detached at every depth rather than only at the top.
    """
    request = TransactionRequest.build(
        request_id="R1",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_identity(),
        scope_claims={ScopeKey.frame("A"): ClaimMode.EXCLUSIVE},
        metadata={"ids": ["a", "b"], "nested": {"deep": [1, 2]}},
    )
    assert request.metadata["ids"] == ("a", "b")
    assert request.metadata["nested"]["deep"] == (1, 2)
    with pytest.raises(TypeError):
        request.metadata["nested"]["deep"] = ()
    assert not hasattr(request.metadata["ids"], "append")


def test_default_metadata_is_frozen_not_a_fresh_mutable_dict():
    """`field(default_factory=dict)` would hand back an editable mapping."""
    staged = StagedTransaction(
        request_id="R1",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter_kind="crystallizer",
        submitter_id="loader",
        admitted_at=0.0,
    )
    assert staged.metadata == {}
    with pytest.raises(TypeError):
        staged.metadata["sneak"] = 1


# --------------------------------------------------------------------------
# _RollbackAction: the one complex-typed record in the package
# --------------------------------------------------------------------------

def test_rollback_action_is_cleanable_and_releases_its_closure():
    """
    A record owning a `Callable` must be able to let go of it on command.

    This is why it is a `Cleanable` class and not a value dataclass: a closure
    transitively pins whatever its defining scope held.
    """
    from melder.aether.aetheric_mediator.transaction_session import _RollbackAction

    entry = _RollbackAction(action=lambda: None, description="undo")
    assert not entry.cleaned
    assert entry.description == "undo"
    entry.cleanup()
    assert entry.cleaned
    assert not hasattr(entry, "action"), "the closure must be released"


def test_rollback_action_cleanup_is_idempotent():
    """A second release must not raise on already-deleted slots."""
    from melder.aether.aetheric_mediator.transaction_session import _RollbackAction

    entry = _RollbackAction(action=lambda: None, description="undo")
    entry.cleanup()
    entry.cleanup()
    assert entry.cleaned


# --------------------------------------------------------------------------
# Participant roster
#
# Aether pushes this plane down into Crystallizer, MutationResearch and Nexus,
# and each announces itself here. The direction is the whole point: the plane
# never reaches out, so it never needs to import `melder.aether`.
# --------------------------------------------------------------------------

def test_registering_is_idempotent_and_reports_first_arrival():
    """An activate/deactivate/activate cycle must be safe to repeat blindly."""
    plane = Mediator(max_wait_seconds=0.1)
    try:
        assert plane.register_participant("crystallizer") is True
        assert plane.register_participant("crystallizer") is False
        assert plane.has_participant("crystallizer")
        assert plane.unregister_participant("crystallizer") is True
        assert plane.unregister_participant("crystallizer") is False
        assert not plane.has_participant("crystallizer")
        assert plane.register_participant("crystallizer") is True
    finally:
        plane.cleanup()


def test_the_roster_answers_which_subsystems_are_live():
    """The plane can name the live subsystems without referencing any of them."""
    plane = Mediator(max_wait_seconds=0.1)
    try:
        for name in ("nexus", "crystallizer", "mutation_research"):
            plane.register_participant(name)
        assert plane.participants() == (
            "crystallizer", "mutation_research", "nexus",
        )
        plane.unregister_participant("nexus")
        assert plane.participants() == ("crystallizer", "mutation_research")
    finally:
        plane.cleanup()


def test_registering_grants_no_claim():
    """
    The roster is not admission. Announcing must not reserve anything.

    If registration ever started taking a claim, a subsystem coming up would
    silently begin blocking transactions it has no business blocking.
    """
    plane = Mediator(max_wait_seconds=0.1)
    try:
        plane.register_participant("crystallizer")
        assert plane.describe()["claims"]["scope_count"] == 0
        assert plane.describe()["admission"]["in_flight_count"] == 0
    finally:
        plane.cleanup()


def test_an_unnameable_participant_is_refused():
    """
    A blank name would not match any `ScopeKey.subsystem(...)` key.

    Silently accepting one produces a roster entry nothing can ever claim
    against, which reads as "the subsystem is live" while being unreachable.
    """
    plane = Mediator(max_wait_seconds=0.1)
    try:
        with pytest.raises(ValueError):
            plane.register_participant("")
        with pytest.raises(ValueError):
            plane.register_participant("   ")
    finally:
        plane.cleanup()


def test_the_roster_is_visible_in_the_plane_snapshot():
    """`describe()` must answer 'who is live' beside 'what is happening'."""
    plane = Mediator(max_wait_seconds=0.1)
    try:
        plane.register_participant("nexus")
        assert plane.describe()["participants"] == ("nexus",)
    finally:
        plane.cleanup()


def test_roster_calls_refuse_after_cleanup():
    """Every roster verb is guarded, like the rest of the plane surface."""
    plane = Mediator(max_wait_seconds=0.1)
    plane.cleanup()
    for call in (
        lambda: plane.register_participant("crystallizer"),
        lambda: plane.unregister_participant("crystallizer"),
        lambda: plane.has_participant("crystallizer"),
        lambda: plane.participants(),
    ):
        with pytest.raises(RuntimeError):
            call()


def test_concurrent_registration_of_one_name_elects_exactly_one_first():
    """
    Free-threaded 3.14t: `first` must be a real election, not a racy read.

    Eight threads announcing the same subsystem must produce exactly ONE True.
    A check-then-set outside the lock would let several threads all believe
    they were first and each run whatever one-time setup that gates.
    """
    plane = Mediator(max_wait_seconds=0.1)
    try:
        barrier = threading.Barrier(8)
        results = []
        results_lock = threading.Lock()

        def announce() -> None:
            """Announce the same participant from every thread at once."""
            barrier.wait()
            outcome = plane.register_participant("crystallizer")
            with results_lock:
                results.append(outcome)

        threads = [threading.Thread(target=announce) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10.0)

        assert len(results) == 8
        assert results.count(True) == 1, (
            "expected exactly one thread to win first-arrival; got {0}. "
            "register_participant is not electing under the lock.".format(
                results.count(True)
            )
        )
    finally:
        plane.cleanup()


# --------------------------------------------------------------------------
# Reference discipline in the claim table
#
# Two records live in this table and they have OPPOSITE answers. A granted
# claim retains a live identity for the span of a claim, so it is Cleanable and
# the TABLE cleans it at teardown - not on release, which is ordinary activity.
# A blocking record is rendered and discarded inside one refusal, so it holds no
# reference at all; removing the reference beats managing one.
# --------------------------------------------------------------------------

def test_blocking_evidence_holds_no_live_identity():
    """
    Evidence outlives the attempt that produced it - it gets logged and kept.

    `AdmissionResult` already requires evidence be "strings, never live
    Identity"; this is the same rule one level down, enforced by there being
    no accessor that could return a claimant.
    """
    table = ClaimTable()
    try:
        holder = _identity("crystallizer", "loader")
        table.try_acquire(holder, {"s1": ClaimMode.EXCLUSIVE})
        blocks = table.try_acquire(_identity("agent", "7"), {"s1": ClaimMode.SHARED})
        assert len(blocks) == 1
        block = blocks[0]
        assert block.holder_description == holder.describe()
        assert not hasattr(block, "holder"), (
            "ClaimBlock exposes a live Identity again; a retained diagnostic "
            "would keep the claimant alive for as long as the message is kept"
        )
    finally:
        table.cleanup()


def test_table_cleanup_cleans_every_granted_record():
    """Teardown releases identities on the cleaning thread, not on the GC."""
    table = ClaimTable()
    holder = _identity()
    table.try_acquire(holder, {"s1": ClaimMode.EXCLUSIVE, "s2": ClaimMode.SHARED})
    granted = [claim for claims in table._claims.values() for claim in claims]
    assert len(granted) == 2
    table.cleanup()
    assert all(claim.cleaned for claim in granted)


def test_granted_claim_cleanup_is_idempotent():
    """The table may sweep a rebuilt list without checking each record first."""
    from melder.aether.aetheric_mediator.claim_table import _GrantedClaim

    claim = _GrantedClaim(holder=_identity(), mode=ClaimMode.EXCLUSIVE)
    claim.cleanup()
    claim.cleanup()
    assert claim.cleaned
    assert not hasattr(claim, "holder")


def test_identity_hashes_and_compares_by_value_while_live():
    """
    Two references to the same claimant are the same claimant.

    Equality and hashing are over `(kind, identity_id)` only - `label` and
    `thread_ident` are presentation and diagnostics.
    """
    first = _identity("crystallizer", "loader")
    second = _identity("crystallizer", "loader")
    registry = {first: "session"}
    assert registry[second] == "session"
    assert first.identity_key() == second.identity_key()


def test_a_cleaned_identity_cannot_corrupt_a_map_keyed_on_identity_key():
    """
    The hazard that used to keep `Identity` out of `Cleanable`, closed at the
    cause rather than argued with.

    `Identity` is CALLER-OWNED, so a subsystem may clean its own identity
    whenever it is finished. The mediator used to key its per-thread session
    maps on the OBJECT, which meant that cleanup made `__hash__` raise and
    corrupted every map still holding it - lookups miss and the entry can
    never be removed.

    `identity_key()` is captured at insertion and is a plain string, so the
    map is immune to whatever happens to the identity afterwards. That is the
    property `Mediator._remember_session` / `_current_session` /
    `_forget_session` now depend on, so it is asserted here directly.
    """
    identity = _identity("crystallizer", "loader")
    key = identity.identity_key()
    sessions = {key: "session"}

    identity.cleanup()

    assert sessions[key] == "session", "the live map must survive its owner"
    assert sessions.pop(key) == "session", "and the entry must stay removable"


def test_a_cleaned_identity_refuses_hashing_and_equality_loudly():
    """
    A cleaned identity has no stable hash, so it must say so.

    The failure has to be a named `RuntimeError` at the point of misuse, not
    an `AttributeError` surfacing from a deleted slot several frames deep
    inside a dict lookup.
    """
    identity = _identity("crystallizer", "loader")
    other = _identity("crystallizer", "loader")
    identity.cleanup()

    with pytest.raises(RuntimeError):
        hash(identity)
    with pytest.raises(RuntimeError):
        identity == other
    with pytest.raises(RuntimeError):
        other == identity
    with pytest.raises(RuntimeError):
        identity.describe()
    with pytest.raises(RuntimeError):
        identity.identity_key()


def test_identity_cleanup_is_idempotent():
    """A caller tearing down may clean unconditionally, as everywhere else."""
    identity = _identity("crystallizer", "loader")
    identity.cleanup()
    identity.cleanup()
    assert identity.cleaned
    assert not hasattr(identity, "_kind")
