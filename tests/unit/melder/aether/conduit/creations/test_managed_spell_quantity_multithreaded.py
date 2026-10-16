"""
Multithreaded tests of ManagedSpellQuantity (STORY-2026-10-15-managed_quantity_pool, S3).

Scope:
    Eight threads lease and release through the same lock-free warm path an emitted plan uses (an idle pop, else
    `reserve` and build) while the pool's cold paths take its leaf lock. The invariants under contention: a
    limited_quantity pool never has more objects alive or out than its limit; a queue pool never hangs and never
    exceeds its limit; an elastic pool's count equals its idle objects once everything is back; a teardown wakes
    every queue waiter. Run under `-X gil=0` and `-X gil=1`.
"""
import threading
from typing import Callable, Dict, List, Optional

from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError


class _SpellStub:
    """The Spell fields a pool reads."""

    def __init__(self, mode: ManagedSpellMode, limit: int, timeout: Optional[float] = None) -> None:
        """
        Keep the options.

        Args:
            mode: The managed mode.
            limit: The managed limit.
            timeout: The queue timeout.
        """
        self.spell_id = "stress-sid"
        self.spell_name = "Stressed"
        # The managed class: the key ReleaseManagedSpell routes releases by (S4).
        self.spell: type = _Worker
        self.binding_name = None
        self.aetheric_frame = "default"
        self.existence = Existence.managed_spell_quantity
        self.disposal_method_names = ["close"]
        self.managed_spell_mode = mode
        self.managed_spell_limit = limit
        self.managed_spell_timeout_seconds = timeout
        self.managed_spell_reset_methods = ("reset",)


class _Worker:
    """A pooled object with a reset and a disposal method."""

    def reset(self) -> None:
        """Nothing to clear."""

    def close(self) -> None:
        """Nothing to release."""


class _OutTracker:
    """Counts objects out at once under its own lock and keeps the peak."""

    def __init__(self) -> None:
        """Start at zero."""
        self._lock = threading.Lock()
        self.out = 0
        self.peak = 0

    def leased(self) -> None:
        """One more object out."""
        with self._lock:
            self.out += 1
            self.peak = max(self.peak, self.out)

    def returned(self) -> None:
        """One object back."""
        with self._lock:
            self.out -= 1


def _lease(pool: ManagedSpellQuantity) -> object:
    """
    Lease like an emitted plan: an idle pop, else reserve a place and build.

    Args:
        pool: The pool.

    Returns:
        object: The leased object.
    """
    try:
        return pool._idle.pop()
    except IndexError:
        served = pool.reserve()
        return _Worker() if served is None else served


def _run_threads(count: int, body: Callable[[], None], timeout: float = 60.0) -> List[BaseException]:
    """
    Run `body` on `count` threads released together and return the errors they raised.

    Args:
        count: Thread count.
        body: Work for each thread.
        timeout: Join timeout per thread; a thread still alive after it is a hang.

    Returns:
        List[BaseException]: Errors raised by the bodies.
    """
    errors: List[BaseException] = []
    errors_lock = threading.Lock()
    start = threading.Barrier(count)

    def _runner() -> None:
        start.wait()
        try:
            body()
        except BaseException as error:
            with errors_lock:
                errors.append(error)

    threads = [threading.Thread(target=_runner, daemon=True) for _ in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout)
        assert not thread.is_alive(), "a worker hung"
    return errors


def test_limited_quantity_never_exceeds_its_limit_under_eight_threads() -> None:
    """Objects alive and objects out stay at or below the limit; refusals are the only failures."""
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.limited_quantity, 3), owner_conduit_id="root")
    tracker = _OutTracker()
    refusals: Dict[str, int] = {"count": 0}
    refusals_lock = threading.Lock()
    peak_count = {"value": 0}

    def _body() -> None:
        for _ in range(400):
            try:
                obj = _lease(pool)
            except ManagedSpellExhaustedError:
                with refusals_lock:
                    refusals["count"] += 1
                continue
            tracker.leased()
            with refusals_lock:
                peak_count["value"] = max(peak_count["value"], pool.count)
            tracker.returned()
            pool.put_back(obj)

    assert _run_threads(8, _body) == []
    assert tracker.peak <= 3
    assert peak_count["value"] <= 3
    assert pool.count <= 3
    assert pool.count == pool.idle_count


def test_queue_never_hangs_and_never_exceeds_its_limit() -> None:
    """With a generous timeout every lease is served by a build below the limit or by a release."""
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.queue, 2, timeout=20.0), owner_conduit_id="root")
    tracker = _OutTracker()

    def _body() -> None:
        for _ in range(300):
            obj = _lease(pool)
            tracker.leased()
            tracker.returned()
            pool.put_back(obj)

    assert _run_threads(8, _body) == []
    assert tracker.peak <= 2
    assert pool.count <= 2
    assert pool.count == pool.idle_count


def test_elastic_count_matches_its_idle_objects_once_everything_is_back() -> None:
    """Elastic never refuses; with at most eight out at once nothing is trimmed and every object comes back."""
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.elastic, 256), owner_conduit_id="root")

    def _body() -> None:
        for _ in range(500):
            pool.put_back(_lease(pool))

    assert _run_threads(8, _body) == []
    assert 1 <= pool.count <= 8
    assert pool.count == pool.idle_count


def test_cleanup_wakes_every_queue_waiter() -> None:
    """Six waiters blocked on a full queue pool all raise the torn-down error when the root tears it down."""
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.queue, 1, timeout=60.0), owner_conduit_id="root")
    _lease(pool)
    started = threading.Barrier(7)
    outcomes: List[BaseException] = []
    outcomes_lock = threading.Lock()

    def _waiter() -> None:
        started.wait()
        try:
            _lease(pool)
        except BaseException as error:
            with outcomes_lock:
                outcomes.append(error)

    threads = [threading.Thread(target=_waiter, daemon=True) for _ in range(6)]
    for thread in threads:
        thread.start()
    started.wait()
    threading.Event().wait(0.1)
    pool.cleanup()
    for thread in threads:
        thread.join(10.0)
        assert not thread.is_alive(), "a waiter hung through teardown"
    assert len(outcomes) == 6
    assert all(
        isinstance(error, RuntimeError) and "was torn down with its root conduit" in str(error) for error in outcomes
    )


def test_releases_racing_a_queue_waiter_hand_over_each_object_once() -> None:
    """Concurrent releases and waiting leases: every lease gets an object no other lease holds at the same time."""
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.queue, 1, timeout=20.0), owner_conduit_id="root")
    holders: Dict[int, int] = {}
    holders_lock = threading.Lock()
    clashes: List[int] = []

    def _body() -> None:
        for _ in range(200):
            obj = _lease(pool)
            with holders_lock:
                if holders.get(id(obj), 0):
                    clashes.append(id(obj))
                holders[id(obj)] = holders.get(id(obj), 0) + 1
            with holders_lock:
                holders[id(obj)] -= 1
            pool.put_back(obj)

    assert _run_threads(8, _body) == []
    assert clashes == []
    assert pool.count == 1
