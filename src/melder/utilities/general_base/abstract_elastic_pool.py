from collections import deque
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Deque, Dict, Generic, Optional, TypeVar

from melder.utilities.general_base.cleanable import Cleanable


_T = TypeVar("_T")


class AbstractElasticPool(Generic[_T], Cleanable, ABC):
    """
    Reusable bounded elastic object-pool base.

    Purpose:
        Provide one shared pooling policy surface for expensive reusable runtime
        objects such as lesser conduits and spellspaces without binding the base
        class to one specific object type.

    Responsibilities:
        - Own the elastic sizing policy: stretch on demand, decay when quiet.
        - Hand out idle objects on `acquire(...)` or create one on miss.
        - Retain released objects only while under both `target_idle` and
          `max_idle`, and destroy the overflow immediately.
        - Leave object creation and destruction abstract for subclasses.

    High-level model:
        - The pool tracks a mutable `target_idle` count.
        - New demand stretches `target_idle` upward by percentage.
        - Quiet periods decay `target_idle` back toward `baseline_idle`.
        - Released objects are retained only while idle count remains below both
          `target_idle` and `max_idle`.
        - Excess returned objects are destroyed immediately instead of retained.

    Contract:
        - `acquire(...)` either reuses an idle object or creates a new one.
        - `release(obj)` appends first, then trims overflow against the current
          elastic target.
        - `cleanup()` destroys all retained idle objects and permanently retires
          the pool.
        - Subclasses define object creation and destruction behavior.

    Threading:
        - Idle deque operations rely on the deque's own operation safety.
        - Stretch, decay, and in-use counters are advisory runtime state and
          may race under concurrent traffic. This is deliberate: they steer
          pool sizing, they do not gate correctness, so paying for a lock on
          every acquire would cost more than the drift is worth.
        - Cleanup remains serialized through `_lock` because it is the
          destructive lifecycle boundary for retained idle objects.

    Lifecycle / Cleanup:
        Inherits the `Cleanable` contract. `cleanup()` destroys every retained
        idle object and permanently retires the pool - it is one-way, and a
        retired pool does not resume serving. Objects currently in use are NOT
        reclaimed by pool cleanup; their owners release them, and those releases
        find a retired pool and destroy rather than retain. Serialized through
        `_lock` because it is the destructive lifecycle boundary.

    Registration:
        GUARDED, and safely so. `AbstractElasticPool` is present in the
        generated `INTERNAL_MANIFEST`, so binding it directly is refused.
        Enforcement is an EXACT `(module, qualname)` test that does NOT walk the
        MRO, so a pool a user writes carries its own identity, misses the
        manifest, and binds normally.

        HISTORICAL: this base was previously excluded, and so was `Cleanable`,
        which it inherits - under the retired `__melder_internal__` sentinel the
        exclusion had to hold at EVERY level of the chain, because `getattr`
        walked the MRO and a single tagged ancestor poisoned every descendant.
        That whole-chain constraint is gone. Exact-match lookup makes each class
        answer only for itself, so `Cleanable` and this class are both guarded
        while user-written pools below them remain bindable (owner ruling
        2026-07-24: guard every class, no exclusion list). No class carries a
        sentinel attribute any more; nothing reads one.

    Subsystem Context:
        One of three `utilities/general_base/` base classes, alongside
        `Cleanable` (teardown contract, which this extends) and `Sync`
        (synchronization mix-in). This is the pooling policy surface: it owns
        the stretch/decay/trim algorithm and leaves object creation and
        destruction abstract. Its in-tree descendants pool the expensive
        reusable runtime objects - lesser conduits and spellspaces - which the
        Conduit runtime acquires per request.

    System Context:
        Beneath the DGR and outside the boot order, but load-bearing for
        resolution throughput: `Conduit` owns one `SpellSpacePool` and one
        `ConduitPool`, so every request-local spellspace and every reused lesser
        conduit passes through this policy. Pool behavior therefore shows up as
        meld latency, which is why the counters are advisory rather than locked.
    """

    _DEFAULT_BASELINE_IDLE: ClassVar[int] = 0
    _DEFAULT_STRETCH_PERCENT: ClassVar[int] = 200
    _DEFAULT_SETTLE_TIME_SECONDS: ClassVar[float] = 1800.0
    _DEFAULT_DECAY_PERCENT_PER_INTERVAL: ClassVar[int] = 10
    _DEFAULT_DECAY_INTERVAL_SECONDS: ClassVar[float] = 600.0

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Base elastic object pool. Subclass this to pool "
        "expensive reusable objects; implement create_object/destroy_object and "
        "the pool handles stretch, decay, and overflow trimming. Deliberately "
        "not registration-guarded so user subclasses stay bindable."
    )

    __slots__ = Cleanable.__slots__ + [
        "_baseline_idle",
        "_decay_interval_seconds",
        "_decay_percent_per_interval",
        "_decay_step",
        "_idle",
        "_in_use_count",
        "_last_decay_at",
        "_last_expand_at",
        "_lock",
        "_max_idle",
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
                Idle target the pool decays back down to.
            stretch_percent:
                Percent used to expand `target_idle` when demand exceeds the
                current prepared capacity.
            settle_time_seconds:
                Cooldown after the last stretch before decay begins.
            decay_percent_per_interval:
                Percent used to decay `target_idle` toward baseline on each
                decay interval.
            decay_interval_seconds:
                Interval between decay steps once cooldown has elapsed.
            max_idle:
                Hard ceiling on retained idle objects. Defaults to
                `baseline_idle` when omitted.
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

        now = (time.monotonic if time_func is None else time_func)()
        self._baseline_idle: int = baseline_idle
        self._stretch_percent: int = stretch_percent
        self._settle_time_seconds: float = settle_time_seconds
        self._decay_percent_per_interval: int = decay_percent_per_interval
        self._decay_interval_seconds: float = decay_interval_seconds
        self._max_idle: int = resolved_max_idle
        self._target_idle: int = baseline_idle
        self._decay_step: int = max(
            1,
            int(
                float(max(baseline_idle, 1))
                * (float(self._decay_percent_per_interval) / 100.0)
            ),
        )
        self._idle: Deque[_T] = deque()
        self._in_use_count: int = 0
        self._lock: threading.RLock = threading.RLock()
        self._time_func: Callable[[], float] = time.monotonic if time_func is None else time_func
        self._last_expand_at: float = now
        self._last_decay_at: float = now

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
            - ADVISORY snapshot read WITHOUT the lock (deque length); may drift
              under concurrent acquire/release, matching the class threading
              model.

        Returns:
            int: Objects currently pooled and available for reuse.
        """
        
        return len(self._idle)

    @property
    def in_use_count(self) -> int:
        """
        Return the number of objects currently checked out of the pool.

        Contract:
            - ADVISORY counter read without the lock; steers sizing, does not
              gate correctness, so it may race under concurrent traffic.

        Returns:
            int: Objects currently checked out.
        """
        
        return self._in_use_count

    @property
    def target_idle(self) -> int:
        """
        Return the current elastic idle-retention target.

        Contract:
            - ADVISORY: mutated by stretch/decay bookkeeping without the lock,
              so it reflects a recent-but-not-instantaneous target.

        Returns:
            int: The idle count the pool is currently steering toward.
        """
        
        return self._target_idle

    @property
    def baseline_idle(self) -> int:
        """
        Return the baseline idle-retention floor.

        Contract:
            - Fixed at construction; `target_idle` never decays below it.

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
              never stretches above it and released overflow is destroyed.

        Returns:
            int: The ceiling above which idle objects are destroyed rather than kept.
        """
        
        return self._max_idle

    def acquire(self, *args: Any, **kwargs: Any) -> _T:
        """
        Acquire one pooled object for use.

        Contract:
            - Reuses an idle object when available by popping directly from the
              idle deque.
            - Creates a new object when direct dequeue pop misses.
            - Applies best-effort stretch bookkeeping only after a real miss.
            - Invokes `prepare_object(...)` on the object before returning it.

        Returns:
            _T: Prepared pooled object.
        """
        
        created_new = False
        try:
            pooled_object = self._idle.pop()
        except IndexError:
            pooled_object = self.create_object(*args, **kwargs)
            created_new = True
        self._in_use_count += 1
        if created_new:
            self._advisory_stretch_after_miss()
        return self.prepare_object(pooled_object, *args, **kwargs)

    def release(self, obj: _T) -> None:
        """
        Release one object back to the pool or destroy it.

        Contract:
            - Decrements the advisory in-use count only when it is positive.
            - Appends first, then trims one cold idle object if retained
              capacity was exceeded.
            - Applies best-effort decay bookkeeping only after a real overflow
              trim.

        Args:
            obj: Object being returned.


        Returns:
            None.
        """
        
        if self._in_use_count > 0:
            self._in_use_count -= 1
        self._idle.append(obj)
        if len(self._idle) <= self._target_idle:
            return
        try:
            overflow_object = self._idle.popleft()
        except IndexError:
            return
        self.destroy_object(overflow_object)
        self._advisory_decay_after_overflow()

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

    def _advisory_stretch_after_miss(self) -> None:
        """
        Best-effort stretch of target idle after a real miss.

        Contract:
            - Called only after a new object had to be created.
            - Expands by percentage and caps at `max_idle`.
            - Recomputes the cached decay step once on stretch.
            - Resets the decay timers on stretch.
            - May race with other stretches or decays and only needs to settle
              out eventually.
        """
        if self._target_idle >= self._max_idle:
            return
        now = self._time_func()
        current_target = self._target_idle
        stretch_amount = max(
            1,
            int(float(current_target) * (float(self._stretch_percent) / 100.0)),
        )
        self._target_idle = min(self._max_idle, current_target + stretch_amount)
        self._decay_step = max(
            1,
            int(
                float(self._target_idle)
                * (float(self._decay_percent_per_interval) / 100.0)
            ),
        )
        self._last_expand_at = now
        self._last_decay_at = now

    def _advisory_decay_after_overflow(self) -> None:
        """
        Best-effort decay of target idle after overflow trim.

        Contract:
            - No decay while cooldown is still active after the last stretch.
            - Applies at most one percentage decay step once the interval has
              elapsed.
            - Never decays below `baseline_idle`.
            - May race with other stretches or decays and only needs to settle
              out eventually.
        """
        if self._target_idle <= self._baseline_idle:
            return
        now = self._time_func()
        if now - self._last_expand_at < self._settle_time_seconds:
            return
        if now - self._last_decay_at < self._decay_interval_seconds:
            return
        self._target_idle = max(
            self._baseline_idle,
            self._target_idle - self._decay_step,
        )
        self._last_decay_at = now
