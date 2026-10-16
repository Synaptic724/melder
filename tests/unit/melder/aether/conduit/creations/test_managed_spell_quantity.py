"""
Unit tests of ManagedSpellQuantity, the pool of one managed spell version (STORY-2026-10-15-managed_quantity_pool, S3).

Scope:
    The pool on its own: sizes per mode, the cold `reserve` per mode (accounting, the limited refusal, the queue
    wait), the release (`put_back`: resets, a raising reset, elastic trims and decay on a fake clock), the children
    records (`adopt`, `abandon`, `destroy_object`), teardown (`cleanup`) and `describe`. The emitted plan that leases
    from the pool arrives with S5; `_lease` plays its part here: pop an idle object, else reserve a place and build.
"""
import gc
import threading
import time
import weakref
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _Clock:
    """Mutable fake monotonic clock that drives the elastic retention."""

    def __init__(self, value: float = 0.0) -> None:
        """
        Start at the given reading.

        Args:
            value: The first reading.
        """
        self.value = value

    def __call__(self) -> float:
        """Return the current reading."""
        return self.value


class _SpellStub:
    """The Spell fields a pool reads, for one managed binding."""

    def __init__(
            self,
            *,
            mode: Optional[ManagedSpellMode] = ManagedSpellMode.elastic,
            limit: Optional[int] = 256,
            timeout: Optional[float] = None,
            resets: Tuple[str, ...] = (),
            disposal: Tuple[str, ...] = ("close",),
            existence: Existence = Existence.managed_spell_quantity,
            spell_id: str = "managed-sid",
            spell_name: str = "Pooled",
    ) -> None:
        """
        Keep the identity, the options and the disposal names.

        Args:
            mode: The managed mode.
            limit: The managed limit.
            timeout: The queue timeout.
            resets: The reset method names.
            disposal: The disposal method names.
            existence: The binding's Existence.
            spell_id: The version id.
            spell_name: The display name.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        # The managed class: the key ReleaseManagedSpell routes releases by (S4).
        self.spell: type = _Pooled
        self.binding_name = "pooled"
        self.aetheric_frame = "frame-1"
        self.existence = existence
        self.disposal_method_names = list(disposal)
        self.managed_spell_mode = mode
        self.managed_spell_limit = limit
        self.managed_spell_timeout_seconds = timeout
        self.managed_spell_reset_methods = tuple(resets)


class _Pooled:
    """A pooled object that writes its resets and disposals to a shared log, failing on request."""

    def __init__(self, label: str, log: List[str], *, fail_reset: bool = False, fail_close: bool = False) -> None:
        """
        Keep the label, the log and the failure switches.

        Args:
            label: Name written to the log.
            log: The test's shared, ordered log.
            fail_reset: Whether `reset` raises after logging.
            fail_close: Whether `close` raises after logging.
        """
        self.label = label
        self.log = log
        self.fail_reset = fail_reset
        self.fail_close = fail_close

    def reset(self) -> None:
        """Log one reset, then fail when asked to."""
        self.log.append(f"reset:{self.label}")
        if self.fail_reset:
            raise ValueError(f"reset failed: {self.label}")

    def flush(self) -> None:
        """Log one flush."""
        self.log.append(f"flush:{self.label}")

    def close(self) -> None:
        """Log one disposal, then fail when asked to."""
        self.log.append(f"close:{self.label}")
        if self.fail_close:
            raise OSError(f"close failed: {self.label}")


def _pool(clock: Optional[_Clock] = None, **options: Any) -> ManagedSpellQuantity:
    """
    Build one pool over a stub Spell.

    Args:
        clock: The fake clock; a fresh one at 0 when omitted.
        **options: `_SpellStub` keywords.

    Returns:
        ManagedSpellQuantity: The pool, owned by root "root-1".
    """
    return ManagedSpellQuantity(
        spell=_SpellStub(**options), owner_conduit_id="root-1", time_func=clock if clock is not None else _Clock(),
    )


def _lease(pool: ManagedSpellQuantity, build: Callable[[], object]) -> object:
    """
    Lease the way an emitted plan does: an idle pop, else reserve a place and build.

    Args:
        pool: The pool.
        build: Builds the object when reserve hands back a place.

    Returns:
        object: The leased object.
    """
    try:
        return pool._idle.pop()
    except IndexError:
        served = pool.reserve()
        return build() if served is None else served


def _run_in_thread(target: Callable[[], object]) -> Tuple[threading.Thread, Dict[str, object]]:
    """
    Start `target` on a thread that stores its result or its exception.

    Args:
        target: The callable to run.

    Returns:
        Tuple[threading.Thread, Dict[str, object]]: The started thread and its outcome dict.
    """
    outcome: Dict[str, object] = {}

    def _runner() -> None:
        try:
            outcome["result"] = target()
        except BaseException as error:
            outcome["error"] = error

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    return thread, outcome


def _wait_for_waiter(pool: ManagedSpellQuantity) -> None:
    """Give a queue waiter time to block on the pool's condition."""
    time.sleep(0.05)


# --- sizes and identity ---------------------------------------------------------------------------------------------

def test_elastic_default_keeps_twenty_and_stretches_to_its_limit() -> None:
    """Elastic: the baseline is min(20, limit), the ceiling the limit, like the kernel pools' 20 / 256."""
    pool = _pool()
    assert (pool.baseline_idle, pool.max_idle, pool.target_idle) == (20, 256, 20)


def test_elastic_with_a_small_limit_is_a_fixed_capacity_pool() -> None:
    """Elastic with a limit at or below 20 keeps exactly `limit` idle objects."""
    pool = _pool(limit=8)
    assert (pool.baseline_idle, pool.max_idle) == (8, 8)


def test_limited_quantity_is_fixed_at_its_limit() -> None:
    """limited_quantity holds at most `limit` objects, so its idle band is fixed at the limit."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=3)
    assert (pool.baseline_idle, pool.max_idle) == (3, 3)


def test_queue_is_fixed_at_its_limit() -> None:
    """queue is fixed at its limit too."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=2, timeout=1.0)
    assert (pool.baseline_idle, pool.max_idle) == (2, 2)


def test_a_non_managed_spell_is_refused() -> None:
    """Only a managed spell has a pool."""
    with pytest.raises(ValueError, match="needs an Existence.managed_spell_quantity spell; 'Pooled' is unique"):
        _pool(existence=Existence.unique, mode=None, limit=None)


def test_the_pool_describes_its_spell_and_owner() -> None:
    """Identity, options and the disposal names come from the Spell; the owner from the store."""
    spell = _SpellStub(mode=ManagedSpellMode.queue, limit=4, timeout=2.5, resets=("reset", "flush"))
    pool = ManagedSpellQuantity(spell=spell, owner_conduit_id="root-9")
    assert pool.spell is spell
    assert (pool.spell_id, pool.spell_name, pool.binding_name, pool.frame_name) == (
        "managed-sid", "Pooled", "pooled", "frame-1",
    )
    assert pool.owner_conduit_id == "root-9"
    assert (pool.mode, pool.limit, pool.timeout_seconds) == (ManagedSpellMode.queue, 4, 2.5)
    assert pool.reset_method_names == ("reset", "flush")
    assert pool.disposal_method_names == ("close",)
    assert (pool.count, pool.idle_count) == (0, 0)


# --- reserve: elastic -----------------------------------------------------------------------------------------------

def test_elastic_reserve_counts_a_place_and_returns_none() -> None:
    """Each elastic miss reserves one place for the plan to build into."""
    pool = _pool()
    assert pool.reserve() is None
    assert pool.reserve() is None
    assert pool.count == 2


def test_elastic_never_refuses() -> None:
    """Elastic builds past its limit: the limit caps idle objects, not live ones."""
    pool = _pool(limit=2)
    for _ in range(10):
        assert pool.reserve() is None
    assert pool.count == 10


def test_elastic_reserve_records_pressure_so_a_burst_is_kept() -> None:
    """A miss within the settle time stretches the target: a burst of 25 is kept up to the limit of 30."""
    log: List[str] = []
    pool = _pool(limit=30)
    burst = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(25)]
    for obj in burst:
        pool.put_back(obj)
    assert (pool.idle_count, pool.count, pool.target_idle) == (25, 25, 25)
    assert log == []


def test_elastic_trim_above_the_limit_disposes_the_oldest() -> None:
    """Under pressure only idle objects above the limit are trimmed, oldest first, one per return here."""
    log: List[str] = []
    pool = _pool(limit=22)
    burst = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(25)]
    for obj in burst:
        pool.put_back(obj)
    assert log == ["close:o0", "close:o1", "close:o2"]
    assert (pool.idle_count, pool.count) == (22, 22)


def test_elastic_decay_after_settling_trims_back_toward_twenty() -> None:
    """Once no miss has happened for the settle time, a return decays the target by 10% and trims the surplus."""
    log: List[str] = []
    clock = _Clock(0.0)
    pool = _pool(clock, limit=22)
    burst = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(25)]
    for obj in burst:
        pool.put_back(obj)
    log.clear()
    clock.value = 1800.0
    pool.put_back(_lease(pool, lambda: _Pooled("never", log)))
    assert (pool.target_idle, pool.idle_count, pool.count) == (20, 20, 20)
    assert log == ["close:o3", "close:o4"]


def test_fixed_capacity_elastic_evicts_the_oldest_on_overflow() -> None:
    """An elastic pool with limit 2 destroys the oldest idle object when a third comes back."""
    log: List[str] = []
    pool = _pool(limit=2)
    objects = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(3)]
    for obj in objects:
        pool.put_back(obj)
    assert log == ["close:o0"]
    assert (pool.idle_count, pool.count) == (2, 2)


# --- reserve: limited_quantity --------------------------------------------------------------------------------------

def test_limited_reserve_counts_places_up_to_the_limit() -> None:
    """Below the limit a miss reserves a place."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=2)
    assert pool.reserve() is None
    assert pool.reserve() is None
    assert pool.count == 2


def test_limited_refuses_at_the_limit_with_nothing_idle() -> None:
    """At the limit with every object out, a miss raises before anything is built."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=2)
    pool.reserve()
    pool.reserve()
    with pytest.raises(ManagedSpellExhaustedError) as excinfo:
        pool.reserve()
    error = excinfo.value
    assert isinstance(error, MeldExecutionError)
    assert (error.mode, error.limit, error.timeout_seconds) == ("limited_quantity", 2, None)
    assert (error.spell_id, error.spell_name) == ("managed-sid", "Pooled")
    assert (
        "Managed spell 'Pooled' (limited_quantity, limit 2) has all 2 objects out. Release one with "
        "ReleaseManagedSpell().release(obj) before melding another, or bind it with a higher managed_spell_limit."
    ) in str(error)
    assert pool.count == 2


def test_limited_at_the_limit_serves_an_object_returned_meanwhile() -> None:
    """A release racing the plan's empty pop is served by reserve instead of a refusal."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1)
    first = _lease(pool, lambda: _Pooled("first", log))
    pool._idle.append(first)
    assert pool.reserve() is first
    assert (pool.count, pool.idle_count) == (1, 0)


def test_limited_never_trims_its_idle_objects() -> None:
    """Idle objects of a fixed-capacity mode never exceed the count, so nothing is evicted."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=2)
    objects = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(2)]
    for obj in objects:
        pool.put_back(obj)
    assert log == []
    assert (pool.idle_count, pool.count) == (2, 2)


# --- reserve: queue -------------------------------------------------------------------------------------------------

def test_queue_reserve_counts_places_below_the_limit() -> None:
    """Below the limit a queue miss reserves a place without waiting."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=2, timeout=5.0)
    assert pool.reserve() is None
    assert pool.count == 1


def test_queue_at_the_limit_takes_an_idle_object_at_once() -> None:
    """At the limit an idle object is handed out with no wait."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0)
    first = _lease(pool, lambda: _Pooled("first", log))
    pool._idle.append(first)
    started = time.monotonic()
    assert pool.reserve() is first
    assert time.monotonic() - started < 1.0


def test_queue_raises_at_its_timeout_with_nothing_free() -> None:
    """A waiter that is never served raises once its timeout has passed, and the count does not move."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=0.05)
    pool.reserve()
    started = time.monotonic()
    with pytest.raises(ManagedSpellExhaustedError) as excinfo:
        pool.reserve()
    assert time.monotonic() - started >= 0.05
    error = excinfo.value
    assert (error.mode, error.limit, error.timeout_seconds) == ("queue", 1, 0.05)
    assert (
        "Managed spell 'Pooled' (queue, limit 1) had no object free within 0.05 s. Release one with "
        "ReleaseManagedSpell().release(obj), or bind it with a higher managed_spell_limit or "
        "managed_spell_timeout_seconds."
    ) in str(error)
    assert pool.count == 1


def test_queue_waiter_is_served_by_a_release() -> None:
    """A release hands the object to a waiting lease: the same object, no build."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0)
    first = _lease(pool, lambda: _Pooled("first", log))
    thread, outcome = _run_in_thread(lambda: _lease(pool, lambda: _Pooled("second", log)))
    _wait_for_waiter(pool)
    pool.put_back(first)
    thread.join(5.0)
    assert not thread.is_alive()
    assert outcome == {"result": first}
    assert pool.count == 1


def test_queue_waiter_gets_a_place_when_an_object_is_destroyed() -> None:
    """Destroying an object frees its place; the waiter then builds into it."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0)
    first = _lease(pool, lambda: _Pooled("first", log))
    thread, outcome = _run_in_thread(lambda: _lease(pool, lambda: _Pooled("second", log)))
    _wait_for_waiter(pool)
    pool.destroy_object(first)
    thread.join(5.0)
    assert not thread.is_alive()
    assert outcome["result"].label == "second"
    assert pool.count == 1
    assert log == ["close:first"]


def test_queue_waiter_gets_a_place_when_a_build_is_abandoned() -> None:
    """A failed build gives its place back and wakes a waiter."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0)
    assert pool.reserve() is None
    thread, outcome = _run_in_thread(lambda: _lease(pool, lambda: _Pooled("second", log)))
    _wait_for_waiter(pool)
    pool.abandon([], RuntimeError("the constructor failed"))
    thread.join(5.0)
    assert not thread.is_alive()
    assert outcome["result"].label == "second"
    assert pool.count == 1


def test_queue_waiter_is_woken_by_cleanup_and_raises() -> None:
    """A teardown wakes every waiter; each raises the torn-down error instead of hanging."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=30.0)
    _lease(pool, lambda: _Pooled("first", log))
    thread, outcome = _run_in_thread(lambda: _lease(pool, lambda: _Pooled("second", log)))
    _wait_for_waiter(pool)
    pool.cleanup()
    thread.join(5.0)
    assert not thread.is_alive()
    error = outcome["error"]
    assert isinstance(error, RuntimeError)
    assert str(error) == (
        "The pool of managed spell 'Pooled' was torn down with its root conduit; nothing can be leased from it."
    )


@pytest.mark.parametrize(
    "options",
    [
        {"mode": ManagedSpellMode.elastic},
        {"mode": ManagedSpellMode.limited_quantity, "limit": 2},
        {"mode": ManagedSpellMode.queue, "limit": 2, "timeout": 1.0},
    ],
)
def test_reserve_after_cleanup_raises_the_torn_down_error(options: Dict[str, Any]) -> None:
    """Every mode refuses a lease from a torn-down pool."""
    pool = _pool(**options)
    pool.cleanup()
    with pytest.raises(RuntimeError, match="nothing can be leased from it"):
        pool.reserve()


# --- put_back -------------------------------------------------------------------------------------------------------

def test_put_back_makes_the_object_the_next_lease() -> None:
    """A release appends; the next lease pops the newest (warmest) object, with no build."""
    log: List[str] = []
    pool = _pool()
    first = _lease(pool, lambda: _Pooled("first", log))
    second = _lease(pool, lambda: _Pooled("second", log))
    pool.put_back(first)
    pool.put_back(second)
    assert _lease(pool, lambda: _Pooled("never", log)) is second
    assert _lease(pool, lambda: _Pooled("never", log)) is first
    assert pool.count == 2


def test_put_back_runs_the_reset_names_in_order() -> None:
    """Each reset name runs once, in the bound order, before the object is idle again."""
    log: List[str] = []
    pool = _pool(resets=("flush", "reset"))
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.put_back(obj)
    assert log == ["flush:o", "reset:o"]
    assert pool.idle_count == 1


def test_put_back_without_reset_names_calls_nothing() -> None:
    """A pool without resets returns objects as they are."""
    log: List[str] = []
    pool = _pool()
    pool.put_back(_lease(pool, lambda: _Pooled("o", log)))
    assert log == []


def test_put_back_never_disposes() -> None:
    """Disposal runs only when the pool destroys an object, never on a release."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    pool.put_back(_lease(pool, lambda: _Pooled("o", log)))
    assert "close:o" not in log


def test_a_raising_reset_destroys_the_object_and_propagates() -> None:
    """The object is disposed, its place freed, the reset error raised as is; later resets do not run."""
    log: List[str] = []
    pool = _pool(resets=("reset", "flush"))
    obj = _lease(pool, lambda: _Pooled("o", log, fail_reset=True))
    with pytest.raises(ValueError, match="reset failed: o"):
        pool.put_back(obj)
    assert log == ["reset:o", "close:o"]
    assert (pool.idle_count, pool.count) == (0, 0)


def test_a_raising_reset_with_a_raising_disposal_raises_both() -> None:
    """When the disposal fails too, one ExceptionGroup carries the reset error and the chained disposal error."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    obj = _lease(pool, lambda: _Pooled("o", log, fail_reset=True, fail_close=True))
    with pytest.raises(ExceptionGroup) as excinfo:
        pool.put_back(obj)
    reset_error, disposal_error = excinfo.value.exceptions
    assert isinstance(reset_error, ValueError)
    assert isinstance(disposal_error, RuntimeError)
    assert isinstance(disposal_error.__cause__, OSError)
    assert "using method 'close'" in str(disposal_error)
    assert pool.count == 0


def test_a_raising_reset_disposes_the_children_recorded_for_the_object() -> None:
    """The destroyed object's recorded children are disposed with it, newest first."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    obj = _lease(pool, lambda: _Pooled("o", log, fail_reset=True))
    pool.adopt(obj, [(_Pooled("c1", log), ["close"]), (_Pooled("c2", log), ["close"])])
    with pytest.raises(ValueError):
        pool.put_back(obj)
    assert log == ["reset:o", "close:o", "close:c2", "close:c1"]


def test_put_back_after_cleanup_raises_and_leaves_the_object_alone() -> None:
    """A release into a torn-down pool raises; no reset or disposal runs on the caller's object."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.cleanup()
    with pytest.raises(RuntimeError) as excinfo:
        pool.put_back(obj)
    assert str(excinfo.value) == (
        "The pool of managed spell 'Pooled' was torn down with its root conduit; the object is yours to dispose."
    )
    assert log == []


def test_release_is_put_back() -> None:
    """The base pool's `release` verb is the same release."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.release(obj)
    assert log == ["reset:o"]
    assert pool.idle_count == 1


def test_the_pool_never_builds() -> None:
    """The plan builds on a miss; the pool's own factory refuses."""
    pool = _pool()
    with pytest.raises(RuntimeError, match="never builds an object"):
        pool.create_object()


def test_the_base_acquire_is_refused() -> None:
    """Leasing goes through the plan (an idle pop, else reserve), never the base acquire."""
    pool = _pool()
    with pytest.raises(RuntimeError, match="never through acquire"):
        pool.acquire()


# --- adopt, abandon, destroy ----------------------------------------------------------------------------------------

def test_destroy_disposes_the_object_then_its_children_newest_first() -> None:
    """destroy_object runs the object's disposal methods, then its recorded children's, newest child first."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [(_Pooled("c1", log), ["close"]), (_Pooled("c2", log), ["close"])])
    pool.destroy_object(obj)
    assert log == ["close:o", "close:c2", "close:c1"]
    assert pool.count == 0


def test_adopt_with_no_children_records_nothing() -> None:
    """Only objects with disposal-bearing children get a record."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [])
    assert pool.describe()["children_recorded"] == 0


def test_adopt_keeps_an_earlier_record_under_a_reused_id_for_teardown() -> None:
    """An older record under the same id belonged to an object dropped while out; teardown still disposes it."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [(_Pooled("old", log), ["close"])])
    pool.adopt(obj, [(_Pooled("new", log), ["close"])])
    pool.destroy_object(obj)
    assert log == ["close:o", "close:new"]
    pool.cleanup()
    assert log == ["close:o", "close:new", "close:old"]


def test_destroy_failures_raise_one_group_and_every_method_runs() -> None:
    """A failing disposal method does not stop the others: one chained RuntimeError per failing method."""
    log: List[str] = []
    pool = _pool(disposal=("close", "flush"))
    obj = _lease(pool, lambda: _Pooled("o", log, fail_close=True))
    pool.adopt(obj, [(_Pooled("c", log, fail_close=True), ["close"])])
    with pytest.raises(ExceptionGroup) as excinfo:
        pool.destroy_object(obj)
    assert log == ["close:o", "flush:o", "close:c"]
    errors = excinfo.value.exceptions
    assert len(errors) == 2
    assert all(isinstance(error, RuntimeError) and isinstance(error.__cause__, OSError) for error in errors)
    assert pool.count == 0


def test_destroy_of_an_uncounted_object_never_takes_the_count_below_zero() -> None:
    """Identity is not tracked; a stray object only floors the count at zero."""
    log: List[str] = []
    pool = _pool()
    pool.destroy_object(_Pooled("stray", log))
    assert pool.count == 0


def test_abandon_frees_the_place_and_disposes_the_children() -> None:
    """A failed build gives its place back and disposes the children it built, newest first."""
    log: List[str] = []
    pool = _pool()
    pool.reserve()
    pool.abandon([(_Pooled("c1", log), ["close"]), (_Pooled("c2", log), ["close"])], RuntimeError("build failed"))
    assert log == ["close:c2", "close:c1"]
    assert pool.count == 0


def test_abandon_turns_disposal_failures_into_notes_on_the_build_error() -> None:
    """The build error stays the error; a child that fails to dispose adds a note to it."""
    log: List[str] = []
    pool = _pool()
    pool.reserve()
    error = RuntimeError("build failed")
    pool.abandon([(_Pooled("c", log, fail_close=True), ["close"])], error)
    assert len(error.__notes__) == 1
    assert "managed spell 'Pooled'" in error.__notes__[0]
    assert "using method 'close'" in error.__notes__[0]


def test_abandon_never_takes_the_count_below_zero() -> None:
    """An abandon without a reservation floors the count at zero."""
    pool = _pool()
    pool.abandon([], RuntimeError("build failed"))
    assert pool.count == 0


def test_adopt_into_a_torn_down_pool_disposes_and_raises() -> None:
    """A build that finishes after teardown: its object and children are disposed and the meld learns why."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.cleanup()
    with pytest.raises(RuntimeError, match="was torn down with its root conduit"):
        pool.adopt(obj, [(_Pooled("c", log), ["close"])])
    assert log == ["close:o", "close:c"]


# --- cleanup --------------------------------------------------------------------------------------------------------

def test_cleanup_disposes_idle_objects_then_the_children_of_objects_out_then_orphans() -> None:
    """Idle objects newest first, each with its children; then the records of objects out; then orphans."""
    log: List[str] = []
    pool = _pool()
    idle_1 = _lease(pool, lambda: _Pooled("i1", log))
    idle_2 = _lease(pool, lambda: _Pooled("i2", log))
    out = _lease(pool, lambda: _Pooled("out", log))
    dropped = _lease(pool, lambda: _Pooled("dropped", log))
    pool.adopt(idle_1, [(_Pooled("k1", log), ["close"])])
    pool.adopt(idle_2, [(_Pooled("k2", log), ["close"])])
    pool.adopt(out, [(_Pooled("ko", log), ["close"])])
    pool.adopt(dropped, [(_Pooled("kx", log), ["close"])])
    pool.adopt(dropped, [(_Pooled("ky", log), ["close"])])
    pool.put_back(idle_1)
    pool.put_back(idle_2)
    pool.cleanup()
    assert log == ["close:i2", "close:k2", "close:i1", "close:k1", "close:ky", "close:ko", "close:kx"]


def test_cleanup_aggregates_every_failure_into_one_group() -> None:
    """Every method of every object runs; each failure is one chained RuntimeError in the group."""
    log: List[str] = []
    pool = _pool()
    objects = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log, fail_close=True)) for i in range(2)]
    for obj in objects:
        pool.put_back(obj)
    with pytest.raises(ExceptionGroup) as excinfo:
        pool.cleanup()
    assert log == ["close:o1", "close:o0"]
    assert len(excinfo.value.exceptions) == 2
    assert "managed spell 'Pooled'" in str(excinfo.value)


def test_cleanup_is_idempotent() -> None:
    """A second cleanup disposes nothing again."""
    log: List[str] = []
    pool = _pool()
    pool.put_back(_lease(pool, lambda: _Pooled("o", log)))
    pool.cleanup()
    pool.cleanup()
    assert log == ["close:o"]
    assert pool.cleaned is True


def test_cleanup_leaves_objects_that_are_out_to_their_holders() -> None:
    """An object out is the agent's: teardown does not dispose it."""
    log: List[str] = []
    pool = _pool()
    _lease(pool, lambda: _Pooled("out", log))
    pool.cleanup()
    assert log == []


def test_after_cleanup_describe_and_the_spell_refuse_but_identity_stays_readable() -> None:
    """The live surface refuses; identity and policy scalars remain for the torn-down errors."""
    pool = _pool()
    pool.cleanup()
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        pool.describe()
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        pool.spell
    assert (pool.spell_name, pool.spell_id, pool.limit) == ("Pooled", "managed-sid", 256)


def test_the_pool_keeps_no_reference_to_an_object_out() -> None:
    """Identity is not tracked: an object out is referenced only by its holder (a children record keys by id)."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [(_Pooled("c", log), ["close"])])
    reference = weakref.ref(obj)
    del obj
    gc.collect()
    assert reference() is None


# --- describe -------------------------------------------------------------------------------------------------------

def test_describe_reports_the_mode_the_numbers_and_the_identity() -> None:
    """One detached snapshot per pool: what an agent reads to see what is out and what is idle."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=3, timeout=1.5, resets=("reset",))
    first = _lease(pool, lambda: _Pooled("a", log))
    _lease(pool, lambda: _Pooled("b", log))
    pool.adopt(first, [(_Pooled("c", log), ["close"])])
    pool.put_back(first)
    snapshot = pool.describe()
    assert {key: snapshot[key] for key in (
        "spell_id", "spell_name", "binding_name", "frame_name", "owner_conduit_id", "mode", "limit",
        "timeout_seconds", "reset_method_names", "disposal_method_names", "count", "idle_count", "out_count",
        "children_recorded", "baseline_idle", "max_idle",
    )} == {
        "spell_id": "managed-sid", "spell_name": "Pooled", "binding_name": "pooled", "frame_name": "frame-1",
        "owner_conduit_id": "root-1", "mode": "queue", "limit": 3, "timeout_seconds": 1.5,
        "reset_method_names": ["reset"], "disposal_method_names": ["close"], "count": 2, "idle_count": 1,
        "out_count": 1, "children_recorded": 1, "baseline_idle": 3, "max_idle": 3,
    }
    assert "in_use_count" not in snapshot


# --- more lifecycle and contention edges -----------------------------------------------------------------------------

def test_queue_deadline_is_taken_once_across_wakeups() -> None:
    """Wake-ups that free nothing do not restart the wait: the waiter raises at its original deadline."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=0.3)
    pool.reserve()
    started = time.monotonic()
    finished: Dict[str, float] = {}

    def _wait() -> None:
        try:
            pool.reserve()
        finally:
            finished["at"] = time.monotonic()

    thread, outcome = _run_in_thread(_wait)
    while thread.is_alive() and time.monotonic() - started < 0.9:
        with pool._condition:
            pool._condition.notify_all()
        time.sleep(0.02)
    thread.join(5.0)
    assert isinstance(outcome["error"], ManagedSpellExhaustedError)
    assert finished["at"] - started < 0.75


def test_a_raising_reset_in_a_queue_pool_raises_for_the_releaser_and_frees_a_place_for_a_waiter() -> None:
    """The releaser gets the reset error; the waiter builds into the place the destroyed object freed."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0, resets=("reset",))
    first = _lease(pool, lambda: _Pooled("first", log, fail_reset=True))
    thread, outcome = _run_in_thread(lambda: _lease(pool, lambda: _Pooled("second", log)))
    _wait_for_waiter(pool)
    with pytest.raises(ValueError, match="reset failed: first"):
        pool.put_back(first)
    thread.join(5.0)
    assert not thread.is_alive()
    assert outcome["result"].label == "second"
    assert pool.count == 1


def test_a_raising_reset_in_a_limited_pool_frees_the_place() -> None:
    """After the failed object is destroyed, the next lease at the limit builds instead of being refused."""
    log: List[str] = []
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1, resets=("reset",))
    first = _lease(pool, lambda: _Pooled("first", log, fail_reset=True))
    with pytest.raises(ValueError):
        pool.put_back(first)
    second = _lease(pool, lambda: _Pooled("second", log))
    assert second.label == "second"
    assert pool.count == 1


def test_an_elastic_miss_after_a_quiet_period_stretches_again() -> None:
    """Decay lowers the target; the next burst's misses open a new pressure window and the burst is kept."""
    log: List[str] = []
    clock = _Clock(0.0)
    pool = _pool(clock, limit=30)
    clock.value = 10_000.0
    burst = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(24)]
    for obj in burst:
        pool.put_back(obj)
    assert (pool.target_idle, pool.idle_count, log) == (24, 24, [])


def test_an_elastic_eviction_disposes_the_evicted_objects_children() -> None:
    """A trim destroys the object with its recorded children, newest child first."""
    log: List[str] = []
    pool = _pool(limit=2)
    objects = [_lease(pool, lambda i=i: _Pooled(f"o{i}", log)) for i in range(3)]
    pool.adopt(objects[0], [(_Pooled("k0a", log), ["close"]), (_Pooled("k0b", log), ["close"])])
    for obj in objects:
        pool.put_back(obj)
    assert log == ["close:o0", "close:k0b", "close:k0a"]
    assert pool.describe()["children_recorded"] == 0


def test_an_eviction_that_fails_raises_from_the_release_and_keeps_the_returned_object() -> None:
    """A destroy failure during a trim surfaces from that release; the object just released stays idle."""
    log: List[str] = []
    pool = _pool(limit=1)
    old = _lease(pool, lambda: _Pooled("old", log, fail_close=True))
    new = _lease(pool, lambda: _Pooled("new", log))
    pool.put_back(old)
    with pytest.raises(ExceptionGroup):
        pool.put_back(new)
    assert list(pool._idle) == [new]
    assert pool.count == 1


def test_destroyed_children_are_not_disposed_again_at_teardown() -> None:
    """A record leaves with its object: teardown does not dispose those children a second time."""
    log: List[str] = []
    pool = _pool()
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [(_Pooled("c", log), ["close"])])
    pool.destroy_object(obj)
    pool.cleanup()
    assert log == ["close:o", "close:c"]


def test_children_of_an_object_out_die_once_at_teardown_and_its_late_release_raises() -> None:
    """Teardown disposes the out object's children; its later release raises and disposes nothing more."""
    log: List[str] = []
    pool = _pool(resets=("reset",))
    obj = _lease(pool, lambda: _Pooled("o", log))
    pool.adopt(obj, [(_Pooled("c", log), ["close"])])
    pool.cleanup()
    with pytest.raises(RuntimeError, match="the object is yours to dispose"):
        pool.put_back(obj)
    assert log == ["close:c"]


def test_cleanup_of_an_empty_pool_retires_it_quietly() -> None:
    """Nothing to dispose: no error, the pool is retired, and leases are refused."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=2)
    pool.cleanup()
    assert pool.cleaned is True
    with pytest.raises(RuntimeError, match="nothing can be leased from it"):
        pool.reserve()


def test_managed_class_is_the_bound_class_and_survives_cleanup() -> None:
    """The pool keeps the class the registry keys on, readable after teardown."""
    pool = _pool()
    assert pool.managed_class is _Pooled
    pool.cleanup()
    assert pool.managed_class is _Pooled


def test_a_rebind_moves_the_managed_class() -> None:
    """A rebind under the same id that brings another class object re-points the key."""

    class _Redefined:
        """A redefinition of the managed class."""

    pool = _pool()
    rebound = _SpellStub()
    rebound.spell = _Redefined
    pool._rebind_spell(rebound)
    assert pool.managed_class is _Redefined
    assert pool.spell is rebound
