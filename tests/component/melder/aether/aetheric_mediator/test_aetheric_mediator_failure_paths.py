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
