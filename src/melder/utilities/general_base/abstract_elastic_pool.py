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

    High-level model:
        - The pool tracks a mutable `target_idle` count.
        - New demand stretches `target_idle` upward by percentage.
        - Quiet periods decay `target_idle` back toward `baseline_idle`.
        - Released objects are retained only while idle count remains below both
          `target_idle` and `max_idle`.
        - Excess returned objects are destroyed immediately instead of retained.

    Contract:
        - `acquire(...)` either reuses an idle object or creates a new one.
        - `release(obj)` decrements in-use count and either retains or destroys
          it based on the current elastic target.
        - `cleanup()` destroys all retained idle objects and permanently retires
          the pool.
        - Subclasses define object creation and destruction behavior.

    Threading:
        - Internal policy state is protected by an `RLock`.
        - The abstract lifecycle hooks execute while the lock is held so the
          pool state and the object state transition stay synchronized.
    """

    _DEFAULT_ENABLED: ClassVar[bool] = True
    _DEFAULT_BASELINE_IDLE: ClassVar[int] = 0
    _DEFAULT_STRETCH_PERCENT: ClassVar[int] = 200
    _DEFAULT_SETTLE_TIME_SECONDS: ClassVar[float] = 1800.0
    _DEFAULT_DECAY_PERCENT_PER_INTERVAL: ClassVar[int] = 10
    _DEFAULT_DECAY_INTERVAL_SECONDS: ClassVar[float] = 600.0

    __slots__ = Cleanable.__slots__ + [
        "_baseline_idle",
        "_decay_interval_seconds",
        "_decay_percent_per_interval",
        "_decay_step",
        "_enabled",
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
            enabled: bool = _DEFAULT_ENABLED,
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
            enabled:
                Whether the pool retains released objects or always destroys
                them.
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
        self._enabled: bool = bool(enabled)
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
            del self._idle
        del self._lock


    @property
    def enabled(self) -> bool:
        """
        Return whether this pool currently retains released objects.
        """

        return self._enabled

    @property
    def idle_count(self) -> int:
        """
        Return the current retained idle object count.
        """
        
        return len(self._idle)

    @property
    def in_use_count(self) -> int:
        """
        Return the number of objects currently checked out of the pool.
        """
        
        return self._in_use_count

    @property
    def target_idle(self) -> int:
        """
        Return the current elastic idle-retention target.
        """
        
        return self._target_idle

    @property
    def baseline_idle(self) -> int:
        """
        Return the baseline idle-retention floor.
        """
        
        return self._baseline_idle

    @property
    def max_idle(self) -> int:
        """
        Return the hard idle-retention ceiling.
        """
        
        return self._max_idle

    def acquire(self, *args: Any, **kwargs: Any) -> _T:
        """
        Acquire one pooled object for use.

        Contract:
            - Reuses an idle object when available.
            - Creates a new object when no idle object is available.
            - Expands `target_idle` when current demand exceeds prepared
              capacity.
            - Invokes `prepare_object(...)` on the object before returning it.

        Returns:
            _T: Prepared pooled object.
        """
        
        with self._lock:
            now = self._time_func()
            self._apply_decay_locked(now)
            pooled_object = self._acquire_idle_object_locked()
            created_new = False
            if pooled_object is None:
                created_new = True
                pooled_object = self.create_object(*args, **kwargs)
                self._in_use_count += 1
            if created_new:
                self._maybe_stretch_locked(now)
            return self.prepare_object(pooled_object, *args, **kwargs)

    def release(self, obj: _T) -> None:
        """
        Release one object back to the pool or destroy it.

        Contract:
            - Decrements in-use count exactly once.
            - Applies decay before deciding whether to retain or destroy.
            - Destroys returned objects when pooling is disabled or idle
              retention is already full.

        Args:
            obj: Object being returned.

        Raises:
            RuntimeError:
                If release is called with no matching checked-out object count.
        """
        
        with self._lock:
            if self._in_use_count <= 0:
                raise RuntimeError("release() called with no in-use objects.")
            now = self._time_func()
            self._apply_decay_locked(now)
            if self._retain_released_object_locked(obj, strict=False):
                return
            self.destroy_object(obj)

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic snapshot of the pool state.

        Returns:
            Dict[str, Any]: Current pool policy and live-count snapshot.
        """
        
        with self._lock:
            return {
                "enabled": self._enabled,
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
        """
        return obj

    def _acquire_idle_object_locked(self) -> Optional[_T]:
        """
        Return one retained idle object and mark it in use.

        Purpose:
            Give specialized pools one shared idle-pop fast path so they can
            reuse the base bookkeeping without re-encoding the same operations
            in each subclass.

        Contract:
            - Call only while holding `_lock`.
            - Returns `None` when pooling is disabled or the idle pool is
              empty.
            - Increments `_in_use_count` exactly once only when an idle object
              is actually reused.

        Returns:
            Optional[_T]:
                Reused idle object when one is available, otherwise `None`.
        """
        if not self._enabled or not self._idle:
            return None
        pooled_object = self._idle.pop()
        self._in_use_count += 1
        return pooled_object

    def _retain_released_object_locked(
            self,
            obj: _T,
            *,
            strict: bool = True,
    ) -> bool:
        """
        Try to retain one released object in the idle pool.

        Purpose:
            Share the core "decrement in-use and append to idle when capacity
            allows" bookkeeping across the generic release path and any
            fixed-capacity pool specializations.

        Contract:
            - Call only while holding `_lock`.
            - Decrements `_in_use_count` exactly once when it is positive.
            - Raises on underflow when `strict=True`.
            - Returns `True` only when the object was retained in `_idle`.
            - Does not destroy the object; callers own the destroy decision
              when retention is not possible.

        Args:
            obj:
                Released object being considered for idle retention.
            strict:
                When `True`, enforce the public release underflow contract.
                Specialized trusted callers may pass `False` to preserve their
                existing soft-underflow behavior.

        Returns:
            bool:
                `True` when the object was retained, otherwise `False`.

        Raises:
            RuntimeError:
                If `strict=True` and the pool has no checked-out object count.
        """
        if self._in_use_count <= 0:
            if strict:
                raise RuntimeError("release() called with no in-use objects.")
        else:
            self._in_use_count -= 1
        if self._enabled and len(self._idle) < self._target_idle:
            self._idle.append(obj)
            return True
        return False

    def _is_fixed_capacity_target_locked(self) -> bool:
        """
        Return whether the current retention target is effectively fixed.

        Purpose:
            Let specialized pools skip stretch and decay work when the current
            runtime policy is already pinned to a fixed-capacity retained-idle
            target.

        Contract:
            - Call only while holding `_lock`.
            - Returns `True` only when the current target matches both the
              baseline and the hard idle ceiling.

        Returns:
            bool:
                `True` when the current policy behaves as a fixed-capacity
                pool, otherwise `False`.
        """
        return (
            self._enabled
            and self._target_idle == self._baseline_idle
            and self._target_idle == self._max_idle
        )

    @abstractmethod
    def create_object(self, *args: Any, **kwargs: Any) -> _T:
        """
        Create one new object for this pool.
        """
        raise NotImplementedError

    @abstractmethod
    def destroy_object(self, obj: _T) -> None:
        """
        Permanently destroy one object that should not be retained.
        """
        raise NotImplementedError

    def _maybe_stretch_locked(self, now: float) -> None:
        """
        Increase target idle only after real capacity breach.

        Contract:
            - Called only after a new object had to be created.
            - Uses the updated checked-out object count to decide whether
              demand breached the retained target.
            - Expands by percentage and caps at `max_idle`.
            - Recomputes the cached decay step once on stretch.
            - Resets the decay timers on stretch.
        """
        if not self._enabled:
            return
        if self._in_use_count <= self._target_idle:
            return
        if self._target_idle >= self._max_idle:
            return
        current_target = max(self._target_idle, self._baseline_idle)
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

    def _apply_decay_once_locked(self, now: float) -> None:
        """
        Apply at most one decay step when the cooldown and interval allow it.

        Contract:
            - No decay while cooldown is active after the last stretch.
            - No decay when the target is already at baseline.
            - Applies one percentage-based decay step and updates the decay
              timestamp to `now`.
        """
        if not self._enabled:
            return
        if self._target_idle <= self._baseline_idle:
            return
        if now - self._last_expand_at < self._settle_time_seconds:
            return
        if now - self._last_decay_at < self._decay_interval_seconds:
            return
        self._target_idle = max(
            self._baseline_idle,
            self._target_idle - self._decay_step,
        )
        self._last_decay_at = now

    def _apply_decay_locked(self, now: float) -> None:
        """
        Decay target idle back toward baseline after quiet periods.

        Contract:
            - No decay while cooldown is still active after the last stretch.
            - Decays in percentage steps at fixed intervals.
            - Never decays below `baseline_idle`.
        """
        if not self._enabled:
            return
        if self._target_idle <= self._baseline_idle:
            return
        if now - self._last_expand_at < self._settle_time_seconds:
            return
        elapsed_since_decay = now - self._last_decay_at
        if elapsed_since_decay < self._decay_interval_seconds:
            return

        steps = int(elapsed_since_decay // self._decay_interval_seconds)
        for _ in range(steps):
            if self._target_idle <= self._baseline_idle:
                break
            self._target_idle = max(
                self._baseline_idle,
                self._target_idle - self._decay_step,
            )
        self._last_decay_at += float(steps) * self._decay_interval_seconds
