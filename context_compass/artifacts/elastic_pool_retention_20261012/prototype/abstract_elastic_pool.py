from collections import deque
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Deque, Dict, Generic, List, Optional, TypeVar

from melder.utilities.general_base.cleanable import Cleanable


_T = TypeVar("_T")


class AbstractElasticPool(Generic[_T], Cleanable, ABC):
    """
    Reusable elastic object-pool base.

    Purpose:
        Provide one shared retention policy for expensive reusable runtime
        objects such as lesser conduits and spellspaces without binding the base
        class to one specific object type.

    Responsibilities:
        - Hand out idle objects on `acquire(...)`, or create one on a miss.
        - Keep returned objects up to a `target_idle` that follows the demand the
          pool actually saw, between `baseline_idle` and `max_idle`.
        - Let `target_idle` decay back toward `baseline_idle` on a clock once
          the pool has seen no shortage for a while, destroying the surplus.
        - Leave object creation and destruction abstract for subclasses.

    High-level model (2026-10-12, 0.2.8234):
        - Live objects are elastic: a miss always builds, so the pool never
          caps how many objects exist at once. `target_idle` decides how many
          RETURNED objects are kept for reuse.
        - A miss is demand the idle set could not serve; it records pressure
          (`_note_miss`). While a miss happened within `settle_time_seconds`, a
          return that finds more idle objects than `target_idle` raises the
          target to that idle count, plus `stretch_percent` of it as headroom,
          capped at `max_idle`. A burst of N concurrent objects is therefore
          kept whole (up to `max_idle`) and a repeat of it is served from idle.
        - Once no miss has happened for `settle_time_seconds`, the target drops
          by `decay_percent_per_interval` of its stretched value (at least 1)
          every `decay_interval_seconds`, never below `baseline_idle`; after a
          long quiet period the missed steps apply together. Idle objects above
          the target are destroyed oldest first, at most one decay step's worth
          per return.
        - Fast path: a return that leaves at most `baseline_idle` objects idle
          is one append and one length compare - no clock read, no lock. Above
          that (the elastic band) a return reads the clock and takes `_lock`
          only to stretch, decay or trim.
        - A fixed-capacity pool (`max_idle == baseline_idle`) has nothing to
          stretch or decay: a return above the baseline destroys the oldest
          idle object, with no clock read and no lock, as before 0.2.8234.
        - Through 0.2.8233 a miss grew the target by `stretch_percent` (default
          200) of itself, which reached `max_idle` within a few misses, and decay
          ran only inside a return that overflowed the target, so a quiet pool
          never shrank and an overloaded one shrank at its busiest; the kernel
          pools also pinned `baseline_idle == max_idle` and never called either.

    Contract:
        - `acquire(...)` either reuses an idle object or creates a new one.
        - `release(obj)` keeps the object while the idle set is within the
          current target, otherwise trims the oldest idle objects.
        - `cleanup()` destroys all retained idle objects and permanently retires
          the pool.
        - Subclasses define object creation and destruction behavior. A
          subclass that replaces `acquire`/`release` with its own fast paths
          calls `_note_miss()` after building on a miss and
          `_rebalance_after_return()` when a return leaves more than
          `baseline_idle` objects idle.

    Threading:
        - Idle deque operations rely on the deque's own operation safety.
        - `_note_miss` writes two timestamps without the lock; they are a
          pressure signal, and a racing write only moves the decay clock by the
          width of the race.
        - Stretch, decay and trim run under `_lock`, a leaf: it is held for the
          counter and deque work only, never while `destroy_object` runs.
        - `in_use_count` is maintained by the base `acquire`/`release` only and
          stays advisory: it may race under concurrent traffic and never gates
          retention.
        - Cleanup remains serialized through `_lock` because it is the
          destructive lifecycle boundary for retained idle objects.

    Lifecycle / Cleanup:
        Inherits the `Cleanable` contract. `cleanup()` destroys every retained
        idle object and permanently retires the pool - it is one-way, and a
        retired pool does not resume serving. Objects currently in use are NOT
        reclaimed by pool cleanup, and a return after `cleanup()` is not
        destroyed by the pool either (it lands in the cleared idle deque): owners
        return their objects before the pool retires, as the owning conduit's
        teardown order does for the kernel pools. (Corrected 2026-10-12: this
        said such returns were destroyed; no code path did that.)

    Registration:
        Your subclasses bind normally: manifest lookup is an EXACT
        `(module, qualname)` match and does not inherit.

    Subsystem Context:
        One of three `utilities/general_base/` base classes, alongside
        `Cleanable` (teardown contract, which this extends) and `Sync`
        (synchronization mix-in). This is the pooling policy surface: it owns
        the retention algorithm and leaves object creation and destruction
        abstract. Its in-tree descendants pool the expensive reusable runtime
        objects - lesser conduits and spellspaces - which the Conduit runtime
        acquires per request.

    System Context:
        Beneath the DGR and outside the boot order, but load-bearing for
        resolution throughput: every `Conduit` owns one `SpellSpacePool` and every
        normal root one `ConduitPool`, so every request-local spellspace and
        every reused lesser conduit passes through this policy. Pool behavior
        therefore shows up as meld latency, which is why the hit and the
        within-baseline return stay lock-free and clock-free.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Base elastic object pool. Subclass this to pool expensive reusable
        objects; implement create_object/destroy_object and the pool keeps what demand needed,
        up to max_idle, and decays back to baseline_idle when demand falls.
    """

    _DEFAULT_BASELINE_IDLE: ClassVar[int] = 0
    _DEFAULT_STRETCH_PERCENT: ClassVar[int] = 0
    _DEFAULT_SETTLE_TIME_SECONDS: ClassVar[float] = 1800.0
    _DEFAULT_DECAY_PERCENT_PER_INTERVAL: ClassVar[int] = 10
    _DEFAULT_DECAY_INTERVAL_SECONDS: ClassVar[float] = 600.0


    __slots__ = Cleanable.__slots__ + [
        "_baseline_idle",
        "_decay_interval_seconds",
        "_decay_percent_per_interval",
        "_decay_step",
        "_idle",
        "_in_use_count",
        "_last_miss_at",
        "_lock",
        "_max_idle",
        "_next_decay_at",
        "_settle_time_seconds",
        "_stretch_percent",
        "_target_idle",
        "_time_func",
    ]

    def __init__(
            self,
            *,
            baseline_idle: int = _DEFAULT_BASELINE_IDLE,
            stretch_percent: int = _DEFAULT_STRETCH_PERCENT,
            settle_time_seconds: float = _DEFAULT_SETTLE_TIME_SECONDS,
            decay_percent_per_interval: int = _DEFAULT_DECAY_PERCENT_PER_INTERVAL,
            decay_interval_seconds: float = _DEFAULT_DECAY_INTERVAL_SECONDS,
            max_idle: Optional[int] = None,
            time_func: Optional[Callable[[], float]] = None,
    ) -> None:
        """
        Initialize the elastic pool policy state.

        Args:
            baseline_idle:
                Idle objects the pool always keeps; the target never decays
                below it, and returns within it take the fast path.
            stretch_percent:
                Headroom, in percent of the observed idle count, added when
                the target stretches under pressure. 0 (the default since
                0.2.8234) keeps exactly what demand built; through 0.2.8233 this
                was the growth per miss, defaulting to 200.
            settle_time_seconds:
                How long after the last miss the pool counts as under
                pressure: returns above the target stretch it, and decay waits.
            decay_percent_per_interval:
                Percent of the stretched target removed per decay step.
            decay_interval_seconds:
                Interval between decay steps once the pool has settled.
            max_idle:
                Hard ceiling on retained idle objects. Defaults to
                `baseline_idle` when omitted (a pool that never stretches).
            time_func:
                Optional monotonic clock supplier for deterministic tests.

        Raises:
            ValueError:
                If any numeric pool parameter is invalid.

        Returns:
            None.
        """
        super().__init__()
        if baseline_idle < 0:
            raise ValueError("baseline_idle must be >= 0.")
        if stretch_percent < 0:
            raise ValueError("stretch_percent must be >= 0.")
        if settle_time_seconds < 0.0:
            raise ValueError("settle_time_seconds must be >= 0.")
        if decay_percent_per_interval < 0:
            raise ValueError("decay_percent_per_interval must be >= 0.")
        if decay_interval_seconds <= 0.0:
            raise ValueError("decay_interval_seconds must be > 0.")

        resolved_max_idle = baseline_idle if max_idle is None else max_idle
        if resolved_max_idle < baseline_idle:
            raise ValueError("max_idle must be >= baseline_idle.")

        clock = time.monotonic if time_func is None else time_func
        now = clock()
        self._baseline_idle: int = baseline_idle
        self._stretch_percent: int = stretch_percent
        self._settle_time_seconds: float = settle_time_seconds
        self._decay_percent_per_interval: int = decay_percent_per_interval
        self._decay_interval_seconds: float = decay_interval_seconds
        self._max_idle: int = resolved_max_idle
        self._target_idle: int = baseline_idle
        self._decay_step: int = max(
            1,
            (max(baseline_idle, 1) * decay_percent_per_interval) // 100,
        )
        self._idle: Deque[_T] = deque()
        self._in_use_count: int = 0
        self._lock: threading.RLock = threading.RLock()
        self._time_func: Callable[[], float] = clock
        # No miss yet: start outside the pressure window, so the first returns
        # above the target trim instead of stretching until demand is seen.
        self._last_miss_at: float = now - settle_time_seconds
        self._next_decay_at: float = now + settle_time_seconds

    def cleanup(self) -> None:
        """
        Destroy all retained idle objects and retire this pool.

        Contract:
            - Idempotent.
            - Destroys only retained idle objects still owned by the pool.
            - Drops all idle references and prevents further acquire/release use.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for obj in self._idle:
                self.destroy_object(obj)
            self._idle.clear()


    @property
    def idle_count(self) -> int:
        """
        Return the current retained idle object count.

        Contract:
            - Snapshot read WITHOUT the lock (deque length); it may move under
              concurrent acquire/release, matching the class threading model.

        Returns:
            int: Objects currently pooled and available for reuse.
        """
        
        return len(self._idle)

    @property
    def in_use_count(self) -> int:
        """
        Return the number of objects currently checked out of the pool.

        Contract:
            - ADVISORY counter read without the lock, maintained by the base
              `acquire`/`release` only (subclass fast paths do not touch it);
              it may race under concurrent traffic and never gates retention.

        Returns:
            int: Objects currently checked out.
        """
        
        return self._in_use_count

    @property
    def target_idle(self) -> int:
        """
        Return the current idle-retention target.

        Contract:
            - Written under `_lock` by stretch and decay, read without it, so a
              read sees a recent value. Always between `baseline_idle` and
              `max_idle`.

        Returns:
            int: The idle count the pool keeps returned objects up to.
        """
        
        return self._target_idle

    @property
    def baseline_idle(self) -> int:
        """
        Return the baseline idle-retention floor.

        Contract:
            - Fixed at construction; `target_idle` never decays below it, and a
              return that leaves at most this many idle objects takes the fast path.

        Returns:
            int: The floor the pool will not shrink below.
        """
        
        return self._baseline_idle

    @property
    def max_idle(self) -> int:
        """
        Return the hard idle-retention ceiling.

        Contract:
            - Fixed at construction (defaults to `baseline_idle`); `target_idle`
              never stretches above it and idle objects beyond it are destroyed.

        Returns:
            int: The ceiling above which idle objects are destroyed rather than kept.
        """
        
        return self._max_idle

    def acquire(self, *args: Any, **kwargs: Any) -> _T:
        """
        Acquire one pooled object for use.

        Contract:
            - Reuses an idle object when available by popping directly from the
              idle deque (the newest return, which is the warmest).
            - Creates a new object when the pop misses, then records the miss as
              pressure (`_note_miss`).
            - Invokes `prepare_object(...)` on the object before returning it.

        Returns:
            _T: Prepared pooled object.
        """
        
        try:
            pooled_object = self._idle.pop()
        except IndexError:
            pooled_object = self.create_object(*args, **kwargs)
            self._note_miss()
        self._in_use_count += 1
        return self.prepare_object(pooled_object, *args, **kwargs)

    def release(self, obj: _T) -> None:
        """
        Release one object back to the pool or destroy it.

        Contract:
            - Decrements the advisory in-use count only when it is positive.
            - Appends first. A return that leaves at most `baseline_idle`
              objects idle ends there (fast path).
            - Above `baseline_idle`, `_rebalance_after_return()` keeps the
              object while the idle set is within the target, stretches the
              target under recent pressure, applies a due decay step, and
              destroys the oldest idle objects above the target.

        Args:
            obj: Object being returned.


        Returns:
            None.
        """
        
        if self._in_use_count > 0:
            self._in_use_count -= 1
        idle = self._idle
        idle.append(obj)
        if len(idle) <= self._baseline_idle:
            return
        self._rebalance_after_return()

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic snapshot of the pool state.

        Returns:
            Dict[str, Any]: Current pool policy and live-count snapshot.
        """
        return {
            "baseline_idle": self._baseline_idle,
            "target_idle": self._target_idle,
            "max_idle": self._max_idle,
            "idle_count": len(self._idle),
            "in_use_count": self._in_use_count,
            "stretch_percent": self._stretch_percent,
            "settle_time_seconds": self._settle_time_seconds,
            "decay_percent_per_interval": self._decay_percent_per_interval,
            "decay_interval_seconds": self._decay_interval_seconds,
            }

    def prepare_object(self, obj: _T, *args: Any, **kwargs: Any) -> _T:
        """
        Prepare one created or reused object before handing it to the caller.

        Purpose:
            Give subclasses a single override point for per-acquire wiring
            without forcing them to replace `acquire(...)`.

        Returns:
            _T: Prepared object. Default implementation returns `obj` unchanged.

        Args:
            obj:
                Pooled object being handed out. Reset per-use state here.
        """
        return obj

    @abstractmethod
    def create_object(self, *args: Any, **kwargs: Any) -> _T:
        """
        Create one new object for this pool.

        Returns:
            _T: A newly constructed pooled object. Subclasses implement this; the pool
                calls it only when no idle object is available.

        Raises:
            NotImplementedError:
                Always on the base; every concrete pool overrides it.
        """
        raise NotImplementedError

    @abstractmethod
    def destroy_object(self, obj: _T) -> None:
        """
        Permanently destroy one object that should not be retained.

        Returns:
            None.

        Args:
            obj:
                Object being permanently discarded. Release its resources here.

        Raises:
            NotImplementedError:
                Always on the base; every concrete pool overrides it.
        """
        raise NotImplementedError

    def _note_miss(self) -> None:
        """
        Record demand the idle set could not serve.

        Purpose:
            A miss is the pool's only evidence that it keeps too few objects.
            It opens (or extends) the pressure window during which returns above
            the target stretch it, and it pushes the next decay step out to one
            settle period after this miss.

        Contract:
            - Called after a new object was built because the idle deque was
              empty: by the base `acquire`, and by subclass fast paths that
              build (or tell their caller to build) on a miss.
            - Writes `_last_miss_at` and moves `_next_decay_at` forward, never back.
            - Builds and destroys nothing.

        Threading:
            Lock-free on purpose: misses already pay for a construction, and
            these two timestamps only steer sizing. A racing write moves the
            decay clock by the width of the race.

        Returns:
            None.
        """
        now = self._time_func()
        self._last_miss_at = now
        settled_at = now + self._settle_time_seconds
        if settled_at > self._next_decay_at:
            self._next_decay_at = settled_at

    def _rebalance_after_return(self) -> None:
        """
        Keep, stretch, decay or trim after a return left more than `baseline_idle` objects idle.

        Purpose:
            The elastic band's entry point. The common case - the idle set is
            within the target and no decay step is due - returns after one clock
            read without taking the lock.

        Contract:
            - Called only after the returned object was appended and the idle
              count exceeded `baseline_idle`.
            - A fixed-capacity pool (`max_idle == baseline_idle`) destroys the
              oldest idle object and returns: no clock read, no lock.
            - Otherwise delegates to `_rebalance_locked` and destroys the surplus
              it hands back, outside the lock, oldest first.
            - If a `destroy_object` call raises, the error propagates unchanged
              (as the one-object eviction's did) and the detached objects not yet
              destroyed go back to the oldest end of the idle deque, so a later
              trim retries them and none is dropped undestroyed.

        Threading:
            The early return is lock-free; the adjustment runs under `_lock`;
            `destroy_object` runs after the lock is released.

        Returns:
            None.
        """
        if self._max_idle == self._baseline_idle:
            # Fixed capacity: the target cannot move, so evict the oldest idle
            # object exactly as the one-overflow return always did - no clock
            # read and no lock on this path.
            try:
                overflow = self._idle.popleft()
            except IndexError:
                return
            self.destroy_object(overflow)
            return
        now = self._time_func()
        if len(self._idle) <= self._target_idle and now < self._next_decay_at:
            return
        surplus = self._rebalance_locked(now)
        destroyed = 0
        try:
            for obj in surplus:
                self.destroy_object(obj)
                destroyed += 1
        finally:
            if destroyed + 1 < len(surplus):
                # A destroy raised: the objects after the failing one were never
                # destroyed; keep them pooled (oldest end, original order).
                self._idle.extendleft(reversed(surplus[destroyed + 1:]))

    def _rebalance_locked(self, now: float) -> List[_T]:
        """
        Adjust the target and detach the idle objects to destroy, under `_lock`.

        Contract:
            - Under pressure (a miss within `settle_time_seconds`): when more
              objects are idle than the target, raise the target to the idle
              count plus `stretch_percent` of it as headroom, capped at
              `max_idle`, and recompute the decay step as
              `decay_percent_per_interval` of the new target (at least 1). Only
              idle objects above `max_idle` are detached: returns racing this
              one stretch the target through their own call, so nothing a burst
              built is destroyed while the burst is still returning.
            - Otherwise, when the decay deadline has passed: lower the target by
              one decay step per elapsed interval (the missed steps of a long
              quiet period apply together), never below `baseline_idle`, and set
              the next deadline one interval out. Idle objects above the target
              are detached.
            - Detaches oldest first, at most one decay step's worth, and returns
              them for destruction.

        Args:
            now: The clock reading the caller took.

        Returns:
            List[_T]: Detached surplus objects for the caller to destroy (often empty).

        Threading:
            Holds `_lock` only for counter and deque work; never calls
            `destroy_object` or any subclass code. Under pressure the next-decay
            deadline is always in the future (`_note_miss` pushed it one settle
            period past the miss), so the decay branch cannot run then.
        """
        surplus: List[_T] = []
        with self._lock:
            idle = self._idle
            target = self._target_idle
            if now - self._last_miss_at < self._settle_time_seconds:
                idle_count = len(idle)
                if idle_count > target:
                    stretched = min(
                        self._max_idle,
                        idle_count + (idle_count * self._stretch_percent) // 100,
                    )
                    if stretched > target:
                        self._target_idle = stretched
                        self._decay_step = max(
                            1,
                            (stretched * self._decay_percent_per_interval) // 100,
                        )
                keep = self._max_idle
            else:
                if now >= self._next_decay_at:
                    if target > self._baseline_idle:
                        steps = 1 + int((now - self._next_decay_at) // self._decay_interval_seconds)
                        target = max(self._baseline_idle, target - steps * self._decay_step)
                        self._target_idle = target
                    self._next_decay_at = now + self._decay_interval_seconds
                keep = target
            excess = len(idle) - keep
            if excess > 0:
                for _ in range(min(excess, self._decay_step)):
                    try:
                        surplus.append(idle.popleft())
                    except IndexError:
                        break
        return surplus
