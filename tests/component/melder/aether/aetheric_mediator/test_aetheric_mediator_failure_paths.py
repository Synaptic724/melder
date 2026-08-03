"""
Component tests for the plane's HARD paths - failure, contention, and races.

The first component file covers the happy paths. This one covers what actually
breaks planes: hooks that raise after claims are held, concurrent multi-scope
acquisition, starvation under the ix/x hierarchy, re-entrant rollback, and
cleanup racing live work.

Two bugs were found by WRITING these before running them, and are guarded here:
  - `begin` leaked claims when a strategy's `on_start` raised, wedging the scope
    forever behind a session no caller ever received.
  - `commit` / `fail` leaked claims when a hook raised, because finalisation ran
    after the hooks instead of in a `finally`.

Run:
    pytest tests/component/melder/aether/aetheric_mediator -q
"""

import contextlib
import gc
import threading
import time

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_session import (
    OutcomePolicy,
    SessionStatus,
    TransactionSession,
)
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy
from melder.aether.aetheric_mediator.transaction_type import TransactionType


class _Hooked(TransactionStrategy):
    """Strategy whose hooks can be armed to raise, per test."""

    raise_on_start = False
    raise_on_end = False
    raise_on_commit_delta = False

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {ScopeKey.frame(metadata["frame"]): ClaimMode.EXCLUSIVE}

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        if _Hooked.raise_on_start:
            raise RuntimeError("on_start exploded")

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        if _Hooked.raise_on_end:
            raise RuntimeError("on_end exploded")

    @classmethod
    def apply_commit_delta(cls, *, information_registry, submitter, staged) -> None:
        if _Hooked.raise_on_commit_delta:
            raise RuntimeError("commit delta exploded")
        super().apply_commit_delta(
            information_registry=information_registry,
            submitter=submitter,
            staged=staged,
        )


class _Hierarchical(TransactionStrategy):
    """Frame-scoped: INTENT on the world parent, EXCLUSIVE on the child."""

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.frame(metadata["frame"]): ClaimMode.EXCLUSIVE,
        }

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        return None

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        return None


class _WholeWorld(TransactionStrategy):
    """Whole-world: EXCLUSIVE on the root scope."""

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {ScopeKey.world(): ClaimMode.EXCLUSIVE}

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        return None

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        return None


@pytest.fixture(autouse=True)
def _disarm_hooks():
    """Reset the armed-hook flags around every case."""
    _Hooked.raise_on_start = False
    _Hooked.raise_on_end = False
    _Hooked.raise_on_commit_delta = False
    yield
    _Hooked.raise_on_start = False
    _Hooked.raise_on_end = False
    _Hooked.raise_on_commit_delta = False


@pytest.fixture()
def plane():
    """A real plane with hooked, hierarchical, and whole-world strategies."""
    built = Mediator(max_wait_seconds=0.25)
    built.strategies.register(
        transaction_type=TransactionType.FORMATION_LOAD, strategy=_Hooked
    )
    built.strategies.register(
        transaction_type=TransactionType.INDEX_GRAFT, strategy=_Hierarchical
    )
    built.strategies.register(
        transaction_type=TransactionType.CHECKPOINT_LOAD, strategy=_WholeWorld
    )
    yield built
    if not built.cleaned:
        built.cleanup()


def _who(identity_id: str) -> Identity:
    """Build a crystallizer-family identity."""
    return Identity(kind="crystallizer", identity_id=identity_id)


# --------------------------------------------------------------------------
# Hook failures must never wedge a scope
# --------------------------------------------------------------------------

def test_on_start_failure_releases_claims_and_reraises(plane):
    """REGRESSION: a raising on_start left the scope claimed forever."""
    _Hooked.raise_on_start = True
    with pytest.raises(RuntimeError, match="on_start exploded"):
        plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("one"),
            metadata={"frame": "A"},
        )
    assert plane.describe()["claims"]["scope_count"] == 0
    assert plane.describe()["admission"]["in_flight_count"] == 0

    _Hooked.raise_on_start = False
    recovered = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("two"),
        metadata={"frame": "A"},
    )
    recovered.leave()
    plane.commit(recovered)


def test_commit_delta_failure_still_releases_claims(plane):
    """REGRESSION: finalisation must run in a finally, not after the hooks."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    session.leave()
    _Hooked.raise_on_commit_delta = True
    with pytest.raises(RuntimeError, match="commit delta exploded"):
        plane.commit(session)
    assert plane.describe()["claims"]["scope_count"] == 0
    assert plane.describe()["admission"]["in_flight_count"] == 0


def test_on_end_failure_on_the_failure_path_still_releases(plane):
    """A transaction that fails twice still has to free its scopes."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    session.leave()
    _Hooked.raise_on_end = True
    with pytest.raises(RuntimeError, match="on_end exploded"):
        plane.fail(session, "stage 6 raised")
    assert plane.describe()["claims"]["scope_count"] == 0


def test_build_start_plan_failure_claims_nothing(plane):
    """A plan that cannot be computed must not half-claim."""

    class _BadPlan(TransactionStrategy):
        @staticmethod
        def build_start_plan(*, submitter, metadata):
            raise ValueError("cannot plan")

        @staticmethod
        def on_start(*, submitter, staged) -> None:
            return None

        @staticmethod
        def on_end(*, submitter, staged) -> None:
            return None

    plane.strategies.register(
        transaction_type=TransactionType.AGENT_REPAIR, strategy=_BadPlan
    )
    with pytest.raises(ValueError, match="cannot plan"):
        plane.begin(
            transaction_type=TransactionType.AGENT_REPAIR, submitter=_who("one")
        )
    assert plane.describe()["claims"]["scope_count"] == 0


# --------------------------------------------------------------------------
# Concurrency: all-or-nothing and the hierarchy under real races
# --------------------------------------------------------------------------

def test_overlapping_multi_scope_acquisition_never_partially_grants():
    """
    Two threads racing OVERLAPPING claim sets in OPPOSITE order.

    This is the classic deadlock/partial-grant shape: A wants {s1,s2}, B wants
    {s2,s1}. Atomic all-or-nothing under one lock means one wins whole and the
    other takes nothing - never a half-set, never a deadlock.
    """
    table = ClaimTable()
    partial = []
    barrier = threading.Barrier(2)

    def worker(name: str, scopes) -> None:
        me = Identity(kind="w", identity_id=name)
        barrier.wait()
        for _attempt in range(200):
            blocks = table.try_acquire(me, scopes)
            held = table.held_scopes(me)
            if blocks and held:
                partial.append((name, held))
            if not blocks:
                if len(held) != 2:
                    partial.append((name, held))
                table.release_holder(me)

    first = threading.Thread(
        target=worker,
        args=("a", {"s1": ClaimMode.EXCLUSIVE, "s2": ClaimMode.EXCLUSIVE}),
    )
    second = threading.Thread(
        target=worker,
        args=("b", {"s2": ClaimMode.EXCLUSIVE, "s1": ClaimMode.EXCLUSIVE}),
    )
    first.start()
    second.start()
    first.join(timeout=30.0)
    second.join(timeout=30.0)
    try:
        assert not first.is_alive() and not second.is_alive(), "deadlocked"
        assert partial == [], "a partial claim set was observed: {0}".format(partial)
        assert table.describe()["scope_count"] == 0
    finally:
        table.cleanup()


def test_whole_world_admits_against_churning_frame_loads(plane):
    """
    STARVATION PROBE - and the measured answer is that it does NOT starve.

    `ix` holders on `world` coexist, so in principle a stream of frame loads
    could keep the parent permanently occupied and starve a whole-world `x`.
    An earlier revision of this test ASSERTED that pessimistic outcome and was
    WRONG: the whole-world claim admits comfortably inside the wait bound.

    The reason is structural rather than lucky. Churning loads hold their `ix`
    only for the duration of one begin/commit cycle, so the parent scope is
    repeatedly and frequently empty, and the waiting `x` is woken by
    `release_holder` the moment the last `ix` drops. Starvation would require
    holders whose lifetimes OVERLAP continuously - long-running loads, not
    churning ones - which is a different and much rarer shape.

    Keeping this as a live probe matters: if a future change makes the plane
    starve under churn, this flips to red and names the regression precisely.
    """
    stop = threading.Event()
    churn_errors = []

    def churn(index: int) -> None:
        while not stop.is_set():
            who = Identity(kind="crystallizer", identity_id="c{0}".format(index))
            try:
                session = plane.begin(
                    transaction_type=TransactionType.INDEX_GRAFT,
                    submitter=who,
                    metadata={"frame": "F{0}".format(index)},
                )
            except RuntimeError:
                continue
            except BaseException as error:  # pragma: no cover - surfaced below
                churn_errors.append("{0}: {1}".format(type(error).__name__, error))
                return
            session.leave()
            plane.commit(session)

    churners = [threading.Thread(target=churn, args=(i,)) for i in range(3)]
    for thread in churners:
        thread.start()
    try:
        time.sleep(0.05)
        started = time.monotonic()
        whole = plane.begin(
            transaction_type=TransactionType.CHECKPOINT_LOAD,
            submitter=_who("whole"),
        )
        waited = time.monotonic() - started
        assert waited < 0.25, (
            "whole-world claim waited {0:.3f}s against churn".format(waited)
        )
        whole.leave()
        plane.commit(whole)
    finally:
        stop.set()
        for thread in churners:
            thread.join(timeout=15.0)
    assert all(not thread.is_alive() for thread in churners)
    assert churn_errors == [], "churn raised unexpectedly: {0}".format(churn_errors)
    assert plane.describe()["claims"]["scope_count"] == 0


def test_continuously_overlapping_intent_holders_do_starve_a_world_claim(plane):
    """
    The OTHER half of the starvation answer, and the honest one.

    Where the churn probe shows no starvation, this shows the shape that DOES:
    two `ix` holders whose lifetimes deliberately overlap, so the parent scope
    is never empty. The whole-world `x` then waits out its bound and refuses
    with evidence.

    This is a REAL PROPERTY OF THE DESIGN, not a bug: `ix` exists precisely so
    piece-work coexists, and the cost is that a parent claim has no priority
    over it. If whole-world claims ever need to pre-empt, that requires an
    explicit fairness mechanism - a queue or a barring flag - which this plane
    deliberately does not have. Documented here so the tradeoff is discovered
    by reading a test rather than by a stalled production load.
    """
    first = plane.begin(
        transaction_type=TransactionType.INDEX_GRAFT,
        submitter=_who("holder-a"),
        metadata={"frame": "A"},
    )
    second = plane.begin(
        transaction_type=TransactionType.INDEX_GRAFT,
        submitter=_who("holder-b"),
        metadata={"frame": "B"},
    )
    try:
        with pytest.raises(RuntimeError) as excinfo:
            plane.begin(
                transaction_type=TransactionType.CHECKPOINT_LOAD,
                submitter=_who("whole"),
            )
        message = str(excinfo.value)
        assert "wait_timeout" in message
        assert ScopeKey.world() in message
    finally:
        first.leave()
        plane.commit(first)
        second.leave()
        plane.commit(second)
    assert plane.describe()["claims"]["scope_count"] == 0


def test_release_wakes_a_waiter_rather_than_leaving_it_to_time_out():
    """A parked waiter must be woken by the release, not by its own timeout."""
    table = ClaimTable()
    holder = Identity(kind="a", identity_id="1")
    table.try_acquire(holder, {"s1": ClaimMode.EXCLUSIVE})
    woke_at = []

    def waiter() -> None:
        started = time.monotonic()
        table.acquire(
            Identity(kind="b", identity_id="2"),
            {"s1": ClaimMode.EXCLUSIVE},
            timeout_seconds=10.0,
        )
        woke_at.append(time.monotonic() - started)

    thread = threading.Thread(target=waiter)
    thread.start()
    time.sleep(0.05)
    table.release_holder(holder)
    thread.join(timeout=10.0)
    try:
        assert not thread.is_alive()
        assert woke_at and woke_at[0] < 5.0, "waiter timed out instead of waking"
    finally:
        table.cleanup()


def test_two_identities_on_one_thread_get_separate_root_sessions(plane):
    """Per-identity sessions: one thread, two actors, two roots."""
    first = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    second = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("two"),
        metadata={"frame": "B"},
    )
    assert first is not second
    assert first.depth == 1 and second.depth == 1
    first.leave()
    plane.commit(first)
    second.leave()
    plane.commit(second)


# --------------------------------------------------------------------------
# Session hard paths
# --------------------------------------------------------------------------

def test_rollback_action_registered_during_unwind_is_not_run(plane):
    """
    Re-entrant registration during unwind must not extend the unwind.

    Inverses run from a snapshot taken under the lock, so an action that
    registers another action cannot cause an unbounded or surprising cascade.
    """
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
        outcome_policy=OutcomePolicy.UNWIND,
    )
    ran = []

    def sneaky() -> None:
        ran.append("sneaky")
        with pytest.raises(RuntimeError):
            session.register_rollback_action(
                action=lambda: ran.append("should not exist"),
                description="late registration",
            )

    session.register_rollback_action(action=sneaky, description="undo sneaky")
    session.leave()
    status, _failures = plane.fail(session, "boom")
    assert status is SessionStatus.ABORTED
    assert ran == ["sneaky"], "a late-registered inverse must not run"
    assert plane.describe()["claims"]["scope_count"] == 0


def test_failing_from_an_inner_scope_is_permitted_and_terminal(plane):
    """
    An inner scope MAY abort the whole transaction.

    This is deliberate and asymmetric with commit: committing from an inner
    scope is refused (an inner success does not mean the outer succeeded), but
    an inner FAILURE must be able to bring the whole transaction down.
    """
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    assert session.depth == 2
    status, _records = plane.fail(session, "inner failure")
    assert status is SessionStatus.ABORTED
    assert plane.describe()["claims"]["scope_count"] == 0


def test_plane_cleanup_while_a_session_is_live_does_not_hang(plane):
    """Tearing down a plane mid-transaction must not strand anything."""
    plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    plane.cleanup()
    assert plane.cleaned is True


def test_cleanup_wakes_a_thread_parked_in_begin(plane):
    """A plane cleaned while a caller waits for admission must free it."""
    held = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("holder"),
        metadata={"frame": "A"},
    )
    assert held is not None
    outcome = []

    def waiter() -> None:
        try:
            plane.begin(
                transaction_type=TransactionType.FORMATION_LOAD,
                submitter=_who("waiter"),
                metadata={"frame": "A"},
            )
            outcome.append("admitted")
        except BaseException as error:
            outcome.append(type(error).__name__)

    thread = threading.Thread(target=waiter)
    thread.start()
    time.sleep(0.05)
    plane.cleanup()
    thread.join(timeout=10.0)
    assert not thread.is_alive(), "caller stranded in begin on a cleaned plane"
    assert outcome, "waiter produced no outcome"

# --------------------------------------------------------------------------
# Deterministic deallocation
#
# This repo is cleanup-based: the thread that finishes with an object frees it
# THEN, not whenever a collector next runs. Reference counting delivers that
# for free - but only for acyclic graphs. A rollback inverse is a closure, and
# a realistic one captures the session it will roll back, which closes the loop
# `session -> _rollback_actions -> _RollbackAction -> closure -> session`.
# Refcounting cannot see through a cycle, so without an explicit break the
# session and everything its closures captured survive until a cycle-collector
# pass on an unrelated schedule.
#
# HOW THESE TESTS PROVE IT. `Cleanable` is slotted and declares no
# `__weakref__`, so sessions cannot be weak-referenced and the usual weakref
# probe is unavailable. Instead a sentinel with a `__del__` is captured by the
# closure: the sentinel's death is observable, and under refcounting it is
# immediate. The cycle collector is DISABLED throughout, which is the whole
# point - with `gc` off the only thing that can free anything is a refcount
# reaching zero, so an observation is proof rather than a timing artefact.
# --------------------------------------------------------------------------

class _Sentinel:
    """Records the moment it is deallocated, so freeing becomes observable."""

    def __init__(self, log, name: str) -> None:
        """Store the shared log and this sentinel's name."""
        self._log = log
        self._name = name

    def __del__(self) -> None:
        """Append this sentinel's name at the instant its refcount hits zero."""
        self._log.append(self._name)


@contextlib.contextmanager
def _gc_off():
    """Run a block with the cycle collector disabled, restoring prior state."""
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()


def _register_capturing_inverses(session, log, count=3):
    """
    Register inverses that close over the session AND a sentinel each.

    Capturing the session is what real inverses do - an undo needs the thing it
    is undoing - and it is what creates the cycle. The sentinel rides along so
    the test can see exactly when that closure is released. The caller keeps no
    reference to either the closure or the sentinel, so the session's rollback
    list is their only owner.
    """
    for index in range(count):
        sentinel = _Sentinel(log, "inverse-{0}".format(index))

        def inverse(bound=session, carried=sentinel) -> None:
            """Touch both captures so neither is optimised out of the cell."""
            bound.describe()
            _ = carried

        session.register_rollback_action(
            action=inverse, description="undo step {0}".format(index)
        )
        del sentinel


def test_commit_frees_the_inverse_closures_before_returning(plane):
    """
    The committing thread releases the closures, not a later collector pass.

    The sentinels must be dead by the time `commit` RETURNS - not merely by the
    time the caller drops the session.
    """
    freed = []
    with _gc_off():
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("committer"),
            metadata={"frame": "A"},
        )
        _register_capturing_inverses(session, freed)
        assert freed == [], "nothing should be freed while the session is open"
        session.leave()
        plane.commit(session)
        assert sorted(freed) == ["inverse-0", "inverse-1", "inverse-2"], (
            "commit returned with the rollback closures still alive; their "
            "teardown has been deferred to the cycle collector"
        )


def test_unwind_frees_the_closures_once_the_inverses_have_run(plane):
    """The UNWIND path releases them too, after running them."""
    freed = []
    with _gc_off():
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("unwinder"),
            metadata={"frame": "A"},
            outcome_policy=OutcomePolicy.UNWIND,
        )
        _register_capturing_inverses(session, freed)
        status, failures = plane.fail(session, "deliberate")
        assert status is SessionStatus.ABORTED
        assert failures == (), "inverses should have run cleanly"
        assert len(freed) == 3, "aborted session retained its closures"


def test_leave_broken_frees_the_closures_after_reporting_residue(plane):
    """
    LEAVE_BROKEN keeps the WORLD's residue, not the session's closures.

    Deliberately leaving structures in place for an agent to repair is a
    statement about the world. The caller still gets the residue - as strings,
    returned before the closures go - so nothing is lost by freeing them.
    """
    freed = []
    with _gc_off():
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("breaker"),
            metadata={"frame": "A"},
            outcome_policy=OutcomePolicy.LEAVE_BROKEN,
        )
        _register_capturing_inverses(session, freed)
        status, residue = plane.fail(session, "left for repair")
        assert status is SessionStatus.BROKEN
        assert len(residue) == 3, "residue must be reported BEFORE the discard"
        assert len(freed) == 3, "broken session retained its closures"


def test_an_unfinalised_session_really_does_leak_without_the_discard():
    """
    DOCUMENTS THE HAZARD the discard exists to prevent.

    A session that registers self-referencing inverses and is never finalised
    holds a true cycle: dropping the last strong reference frees NOTHING while
    the collector is off. Re-enabling the collector proves it was a cycle and
    not a stray reference. This is the exact fate every transaction would meet
    if `_finalize` did not cut the edge.
    """
    freed = []
    with _gc_off():
        plane = Mediator(max_wait_seconds=0.25)
        plane.strategies.register(
            transaction_type=TransactionType.FORMATION_LOAD, strategy=_Hooked
        )
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("leaker"),
            metadata={"frame": "A"},
        )
        _register_capturing_inverses(session, freed)
        del session
        assert freed == [], (
            "expected the cycle to hold everything alive here; if this fires, "
            "the closures are not capturing the session and the rest of these "
            "tests are proving nothing"
        )
        plane.cleanup()
        del plane
    assert gc.collect() >= 0
    assert len(freed) == 3, "collector could not reclaim the cycle either"


def test_finalisation_keeps_the_outcome_readable(plane):
    """
    Discarding inverses must NOT blind the caller to its own result.

    A full `cleanup()` in `_finalize` would trip `check_cleaned()` on every
    accessor, so a caller could not learn whether its own transaction
    committed. Only the cyclic edge is the plane's to cut.
    """
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("reader"),
        metadata={"frame": "A"},
    )
    _register_capturing_inverses(session, [], count=1)
    session.leave()
    plane.commit(session)
    assert not session.cleaned
    assert session.status is SessionStatus.COMMITTED
    assert session.request.request_id
    assert session.describe()["registered_inverses"] == []


def test_discard_refuses_while_the_session_is_open(plane):
    """An OPEN session may still need to unwind, so its inverses must stay."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("open"),
        metadata={"frame": "A"},
    )
    _register_capturing_inverses(session, [], count=2)
    with pytest.raises(RuntimeError):
        session.discard_inverses()
    assert len(session.describe()["registered_inverses"]) == 2
    session.leave()
    plane.commit(session)


def test_discard_is_idempotent_and_reports_once(plane):
    """`_finalize` already discarded, so a caller's own later call is a no-op."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("twice"),
        metadata={"frame": "A"},
    )
    _register_capturing_inverses(session, [], count=2)
    session.leave()
    plane.commit(session)
    assert session.discard_inverses() == ()


def test_failed_begin_cleans_the_session_it_could_not_return(plane):
    """
    A session `begin` never returned is freed by the thread that built it.

    Nobody else can ever hold it, so it is cleaned outright rather than merely
    discarded - and that must happen before the exception propagates.
    """
    _Hooked.raise_on_start = True
    seen = []
    original = TransactionSession.cleanup

    def spy(self) -> None:
        """Record whether cleanup ran, then delegate to the real teardown."""
        seen.append(self.request.request_id)
        original(self)

    TransactionSession.cleanup = spy
    try:
        with pytest.raises(RuntimeError):
            plane.begin(
                transaction_type=TransactionType.FORMATION_LOAD,
                submitter=_who("doomed"),
                metadata={"frame": "A"},
            )
    finally:
        TransactionSession.cleanup = original
    assert len(seen) == 1, "begin did not clean the session it could not return"


def test_staged_record_is_built_once_and_never_restamped(plane):
    """
    One admission, one staged record - identity, not just equality.

    `commit` and `fail` used to rebuild it from the request, which reallocated
    the metadata copy on every call AND restamped `admitted_at` with the commit
    time, making the field report the wrong moment.
    """
    seen = []

    class _Recording(TransactionStrategy):
        """Strategy that records the staged object each hook receives."""

        @staticmethod
        def build_start_plan(*, submitter, metadata):
            """Claim the named frame exclusively."""
            return {ScopeKey.frame(metadata["frame"]): ClaimMode.EXCLUSIVE}

        @staticmethod
        def on_start(*, submitter, staged) -> None:
            """Record the staged record handed to the start hook."""
            seen.append(staged)

        @staticmethod
        def on_end(*, submitter, staged) -> None:
            """Record the staged record handed to the end hook."""
            seen.append(staged)

        @staticmethod
        def apply_commit_delta(*, information_registry, submitter, staged) -> None:
            """Record the staged record handed to the commit delta."""
            seen.append(staged)

    plane.strategies.register(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE, strategy=_Recording
    )
    session = plane.begin(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
        submitter=_who("stamper"),
        metadata={"frame": "A"},
    )
    admitted_at = session.staged.admitted_at
    time.sleep(0.05)
    session.leave()
    plane.commit(session)
    assert len(seen) == 3, "expected on_start, commit delta, and on_end"
    first = seen[0]
    for record in seen[1:]:
        assert record is first, (
            "staged record was rebuilt mid-transaction; that reallocates the "
            "metadata copy and restamps admitted_at with the commit time"
        )
    assert first.admitted_at == admitted_at


# --------------------------------------------------------------------------
# Inverses are released AS THEY RUN, not in a batch at the end
#
# `_RollbackAction` owns a `Callable`, which is the one genuinely complex type
# in this package: a closure pins whatever its defining scope held. DevOps
# treats its own hooks this way - `ChangeControlManager.cleanup` explicitly
# `del`s `_commit_hook`, `_abort_hook` and the rest - so these records are
# `Cleanable` and the unwind releases each one the moment it is done with it.
# --------------------------------------------------------------------------


def _register_sentinel_inverse(session, log, name, explode=False):
    """
    Register one inverse holding a sentinel, leaving NO reference behind.

    THIS MUST BE A FUNCTION, not an inline loop in a test body. A `def` inside
    a test binds the closure to a local name, and the test's own frame then
    keeps that closure - and its sentinel - alive for the rest of the test. A
    loop is worse: the name survives pointing at the LAST closure built, so
    every iteration but the final one looks correctly released and the last one
    looks leaked. That failure is indistinguishable from a real retention bug
    while the production code is perfectly correct. Returning from here drops
    the frame and with it the only stray reference.

    Args:
        session: The session to register the inverse on.
        log: Shared list the sentinel appends its name to when deallocated.
        name: The sentinel's name.
        explode: When True the inverse raises, to exercise the failing path.
    """
    sentinel = _Sentinel(log, name)

    def inverse(carried=sentinel) -> None:
        """Hold the sentinel until this record is released."""
        _ = carried
        if explode:
            raise RuntimeError("inverse exploded")

    session.register_rollback_action(
        action=inverse, description="undo {0}".format(name)
    )


def test_each_inverse_is_released_as_soon_as_it_has_run(plane):
    """
    By the time the last inverse runs, the earlier ones are already freed.

    Inverses run newest-first, so the FIRST action registered runs LAST and can
    observe how much has been released by then. Releasing only after the loop
    would leave every closure alive here and the observation would be zero.
    """
    freed = []
    observed = []
    with _gc_off():
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("stepwise"),
            metadata={"frame": "A"},
            outcome_policy=OutcomePolicy.UNWIND,
        )
        session.register_rollback_action(
            action=lambda: observed.append(len(freed)),
            description="observer, runs last",
        )
        for index in (1, 2):
            _register_sentinel_inverse(session, freed, "inverse-{0}".format(index))
        session.leave()
        plane.fail(session, "boom")
    assert observed == [2], (
        "expected both earlier inverses to be released before the last one "
        "ran; got {0!r}, which means the closures are held for the whole "
        "unwind".format(observed)
    )


def test_a_raising_inverse_does_not_pin_the_remaining_closures(plane):
    """
    The `finally` release is what makes a failing unwind safe.

    A raising inverse produces a caught exception whose traceback references
    the unwind frame - and so the local list of pending records. Releasing in a
    `finally` bounds that to the record in hand.
    """
    freed = []
    with _gc_off():
        session = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("exploder"),
            metadata={"frame": "A"},
            outcome_policy=OutcomePolicy.UNWIND,
        )
        for index in (0, 1):
            _register_sentinel_inverse(session, freed, "inverse-{0}".format(index))
        _register_sentinel_inverse(session, freed, "exploder", explode=True)
        session.leave()
        status, failures = plane.fail(session, "boom")
        assert status is SessionStatus.ABORTED
        assert len(failures) == 1 and "exploded" in failures[0]
        assert sorted(freed) == ["exploder", "inverse-0", "inverse-1"], (
            "a failing inverse retained closures; got {0!r}".format(sorted(freed))
        )


def test_unwind_empties_the_session_list_so_ownership_is_unambiguous(plane):
    """
    `fail` hands the records to the unwind; the session keeps none.

    Two places holding the same records is how a double-release or a missed
    release happens, so ownership transfers outright.
    """
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("owner"),
        metadata={"frame": "A"},
        outcome_policy=OutcomePolicy.UNWIND,
    )
    session.register_rollback_action(action=lambda: None, description="undo")
    session.leave()
    plane.fail(session, "boom")
    assert session.describe()["registered_inverses"] == []
    assert session.discard_inverses() == ()


# --------------------------------------------------------------------------
# Sliced admission waiting (ported from the DevOps plane)
#
# Admission runs THROUGH the orchestrator, so the check and the park are two
# separate acquisitions of the table's condition and the window between them
# cannot be closed by restructuring the loop - closing it would mean holding
# the table lock across the admission call, which is the AB-BA the design
# avoids. `TransactionMediator._admit_with_scope_wait` in DevOps hit this first
# and answered it by slicing each park, so a missed notification costs one
# slice instead of the whole wait budget.
# --------------------------------------------------------------------------

def test_a_release_landing_in_the_admission_window_is_not_slept_through():
    """
    REGRESSION: a release that lands between a refused admission and the park
    that follows it is MISSED, and nothing notifies again until the NEXT
    release. If the blocker was the last holder, there is no next release.

    Before the park was sliced, that cost the FULL `max_wait_seconds` with the
    contended scope sitting free the entire time. This test is single-threaded
    and forces the release into the window by construction, so it cannot pass
    or fail on timing luck.
    """
    plane = Mediator(max_wait_seconds=8.0)
    try:
        plane.strategies.register(
            transaction_type=TransactionType.FORMATION_LOAD, strategy=_Hooked
        )
        blocker = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("blocker"),
            metadata={"frame": "A"},
        )
        blocker.leave()

        fired = []
        real_wait = ClaimTable.wait_for_change

        def release_then_park(self, timeout_seconds):
            """Commit the blocker INSIDE the window, then park as production does."""
            if not fired:
                fired.append(True)
                plane.commit(blocker)
            return real_wait(self, timeout_seconds)

        ClaimTable.wait_for_change = release_then_park
        try:
            started = time.monotonic()
            session = plane.begin(
                transaction_type=TransactionType.FORMATION_LOAD,
                submitter=_who("waiter"),
                metadata={"frame": "A"},
            )
            elapsed = time.monotonic() - started
        finally:
            ClaimTable.wait_for_change = real_wait

        assert fired, (
            "the racing wait never ran, so nothing was proven - the waiter was "
            "admitted without ever being refused"
        )
        session.leave()
        plane.commit(session)

        assert elapsed < 4.0, (
            "admission took {0:.1f}s after a release that landed in the "
            "missed-notification window. The park is not sliced: it is "
            "sleeping out the whole max_wait_seconds budget with the scope "
            "already free.".format(elapsed)
        )
    finally:
        if not plane.cleaned:
            plane.cleanup()


def test_the_wait_slice_never_extends_a_caller_past_its_own_deadline():
    """
    Slicing must bound the MISS, never the total. A caller that asked for a
    short budget must still time out on schedule, not run on in one-second
    slices.
    """
    plane = Mediator(max_wait_seconds=0.4)
    try:
        plane.strategies.register(
            transaction_type=TransactionType.FORMATION_LOAD, strategy=_Hooked
        )
        held = plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("holder"),
            metadata={"frame": "A"},
        )
        started = time.monotonic()
        with pytest.raises(RuntimeError) as excinfo:
            plane.begin(
                transaction_type=TransactionType.FORMATION_LOAD,
                submitter=_who("late"),
                metadata={"frame": "A"},
            )
        elapsed = time.monotonic() - started
        assert "wait_timeout" in str(excinfo.value)
        assert elapsed < 1.0, (
            "a 0.4s budget waited {0:.1f}s - the slice is being treated as a "
            "floor rather than a cap".format(elapsed)
        )
        held.leave()
        plane.commit(held)
    finally:
        if not plane.cleaned:
            plane.cleanup()


# --------------------------------------------------------------------------
# The commit pipeline, ported from DevOps `_finalize_root_session`
#
# Three linked defects lived here before the port, all in the same
# hand-written mechanism:
#   - a failing commit DISCARDED the inverses instead of running them, so
#     `OutcomePolicy.UNWIND` was silently not honoured;
#   - the session reported COMMITTED after its own commit had raised, and
#     `SessionStatus.COMMITTING` was vocabulary nothing ever assigned;
#   - `on_end` was dispatched inside the success path, so a raising commit
#     delta skipped it and any gate a strategy froze in `on_start` leaked.
# --------------------------------------------------------------------------


class _EndCounting(TransactionStrategy):
    """Strategy that counts its own end dispatches and can arm failures."""

    ends = 0
    raise_on_start = False
    raise_on_commit_delta = False

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        """Claim one frame exclusively."""
        return {ScopeKey.frame(metadata["frame"]): ClaimMode.EXCLUSIVE}

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        """Raise when armed, to exercise the post-admission failure path."""
        if _EndCounting.raise_on_start:
            raise RuntimeError("on_start exploded")

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        """Count every dispatch; the law is exactly one per terminal end."""
        _EndCounting.ends += 1

    @classmethod
    def apply_commit_delta(cls, *, information_registry, submitter, staged) -> None:
        """Raise when armed, to exercise the commit-failure path."""
        if _EndCounting.raise_on_commit_delta:
            raise RuntimeError("commit delta exploded")
        super().apply_commit_delta(
            information_registry=information_registry,
            submitter=submitter,
            staged=staged,
        )


@pytest.fixture()
def counting_plane():
    """A plane whose SUBSYSTEM_ACTIVATE family counts its end dispatches."""
    _EndCounting.ends = 0
    _EndCounting.raise_on_start = False
    _EndCounting.raise_on_commit_delta = False
    built = Mediator(max_wait_seconds=0.25)
    built.strategies.register(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE, strategy=_EndCounting
    )
    yield built
    if not built.cleaned:
        built.cleanup()
    _EndCounting.ends = 0
    _EndCounting.raise_on_start = False
    _EndCounting.raise_on_commit_delta = False


def _open(plane, who, policy=OutcomePolicy.UNWIND):
    """Open one SUBSYSTEM_ACTIVATE session already lowered to depth zero."""
    session = plane.begin(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
        submitter=_who(who),
        metadata={"frame": "A"},
        outcome_policy=policy,
    )
    session.leave()
    return session


def test_a_failing_commit_runs_the_inverses_instead_of_discarding_them(
    counting_plane,
):
    """
    UNWIND must mean unwind, including when the COMMIT is what failed.

    The regression: `_finalize` calls `discard_inverses()`, which throws the
    rollback actions away. Before the port the session was already marked
    COMMITTED, so nothing had run them first - the world stayed half-mutated
    and the inverses went in the bin.
    """
    session = _open(counting_plane, "unwinder")
    ran = []
    session.register_rollback_action(
        action=lambda: ran.append("outer"), description="undo outer"
    )
    session.register_rollback_action(
        action=lambda: ran.append("inner"), description="undo inner"
    )
    _EndCounting.raise_on_commit_delta = True

    with pytest.raises(RuntimeError, match="commit delta exploded"):
        counting_plane.commit(session)

    assert ran == ["inner", "outer"], "inverses must run newest-first"
    assert session.status is SessionStatus.ABORTED
    assert "commit delta exploded" in session.failure_reason


def test_a_failing_commit_under_leave_broken_keeps_a_readable_ledger(
    counting_plane,
):
    """
    LEAVE_BROKEN is only meaningful if the ledger outlives finalisation.

    `fail(...)` returns the residue, but on the commit path NOBODY is holding
    that return value - the mediator raises the original error instead. The
    residue is therefore retained on the session, and it has to survive
    `discard_inverses`, which empties `registered_inverses` immediately after.
    """
    session = _open(counting_plane, "breaker", policy=OutcomePolicy.LEAVE_BROKEN)
    ran = []
    session.register_rollback_action(
        action=lambda: ran.append("never"), description="detach conduit 7"
    )
    _EndCounting.raise_on_commit_delta = True

    with pytest.raises(RuntimeError, match="commit delta exploded"):
        counting_plane.commit(session)

    assert ran == [], "LEAVE_BROKEN must run nothing"
    assert session.status is SessionStatus.BROKEN
    assert session.leave_broken_residue == ("detach conduit 7",)
    described = session.describe()
    assert described["leave_broken_residue"] == ["detach conduit 7"]
    assert described["registered_inverses"] == [], (
        "finalisation discards the inverses; the ledger must not go with them"
    )


def test_on_end_fires_exactly_once_when_the_commit_delta_raises(counting_plane):
    """
    A strategy that froze a gate in `on_start` is owed its reopen.

    DevOps dispatches `on_end` from `_finalize_root_session`'s finally for
    exactly this reason. Dispatched inside the success path instead, a raising
    delta skips it and the freeze leaks with no symptom but a stuck gate.
    """
    session = _open(counting_plane, "ender")
    _EndCounting.raise_on_commit_delta = True

    with pytest.raises(RuntimeError, match="commit delta exploded"):
        counting_plane.commit(session)

    assert _EndCounting.ends == 1


def test_on_end_fires_when_on_start_raises(counting_plane):
    """
    A half-run `on_start` owes its reopen too - DevOps ends that session
    through the same finalisation path rather than unwinding it by hand.
    """
    _EndCounting.raise_on_start = True

    with pytest.raises(RuntimeError, match="on_start exploded"):
        counting_plane.begin(
            transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
            submitter=_who("starter"),
            metadata={"frame": "A"},
        )

    assert _EndCounting.ends == 1
    assert counting_plane.describe()["claims"]["scope_count"] == 0


def test_a_failing_commit_still_releases_every_claim(counting_plane):
    """
    Leaving the WORLD broken is a product decision; leaving the CLAIM TABLE
    broken just wedges the plane. Both outcome policies must drain.
    """
    for policy in (OutcomePolicy.UNWIND, OutcomePolicy.LEAVE_BROKEN):
        session = _open(counting_plane, "drainer", policy=policy)
        session.register_rollback_action(
            action=lambda: None, description="something"
        )
        _EndCounting.raise_on_commit_delta = True
        with pytest.raises(RuntimeError, match="commit delta exploded"):
            counting_plane.commit(session)
        described = counting_plane.describe()
        assert described["claims"]["scope_count"] == 0, policy
        assert described["admission"]["in_flight_count"] == 0, policy
        assert described["reporting"]["active_count"] == 0, policy


def test_a_successful_commit_still_passes_through_committing(counting_plane):
    """The happy path must not have been broken by making failure honest."""
    session = _open(counting_plane, "happy")
    counting_plane.commit(session)
    assert session.status is SessionStatus.COMMITTED
    assert session.failure_reason is None
    assert session.leave_broken_residue == ()
    assert _EndCounting.ends == 1
    assert counting_plane.describe()["claims"]["scope_count"] == 0


def test_a_caller_may_clean_its_own_identity_without_harming_the_plane(
    counting_plane,
):
    """
    `Identity` is CALLER-OWNED. The plane borrows it and never cleans it, and
    a caller cleaning its own must not reach into the plane's bookkeeping.

    This is the integration half of the unit-level guard. The mediator keys
    its per-thread session maps on `identity_key()` - a plain string captured
    at insertion - precisely so that a cleaned identity cannot make `__hash__`
    raise inside `_forget_session` and strand an entry that can then never be
    removed. Keyed on the object, the SECOND transaction below would have been
    the failure: the first identity's entry would still be sitting in the map,
    unhashable and unremovable.
    """
    first = _who("owner-cleans")
    session = counting_plane.begin(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
        submitter=first,
        metadata={"frame": "A"},
    )
    session.leave()
    counting_plane.commit(session)

    first.cleanup()

    second = counting_plane.begin(
        transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
        submitter=_who("owner-cleans"),
        metadata={"frame": "A"},
    )
    second.leave()
    counting_plane.commit(second)

    assert second.status is SessionStatus.COMMITTED
    described = counting_plane.describe()
    assert described["claims"]["scope_count"] == 0
    assert described["admission"]["in_flight_count"] == 0
