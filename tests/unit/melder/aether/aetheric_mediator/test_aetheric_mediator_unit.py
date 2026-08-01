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
    """An inner scope must not terminate an outer one."""
    session = _session()
    session.join()
    with pytest.raises(RuntimeError):
        session.mark_committed()


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


