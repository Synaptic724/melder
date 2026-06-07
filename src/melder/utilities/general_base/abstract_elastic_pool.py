from collections import deque
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Deque, Dict, Generic, List, Optional, TypeVar

from melder.utilities.general_base.cleanable import Cleanable


_T = TypeVar("_T")


class AbstractElasticPool(Generic[_T], Cleanable, ABC):
    """
    Reusable burst-oriented idle-shell pool base.

    Purpose:
        Provide one shared coarse burst-pool surface for reusable runtime
        shells such as lesser conduits and spellspaces without binding the base
        class to one concrete object type.

    High-level model:
        - The pool holds only idle reusable shells in `_idle`.
        - Borrowed pressure is tracked through `_borrowed_tickets`.
        - A miss at the current ceiling expands the retained ceiling by one
          coarse burst factor.
        - Returned objects are retained while idle count remains below the
          current ceiling.
        - Once borrowed pressure falls back under the active shrink mark, the
          ceiling is stepped down by one floor increment.
        - Already-idle shells are not retroactively evicted when the ceiling
          drops; only future returns above the current ceiling are cleaned up.
        - No time-based decay runs on the hot path.

    Contract:
        - `acquire(...)` either reuses an idle object or records a miss and
          creates a new one.
        - `release(obj)` pops one borrow ticket when available and either
          retains or destroys the returned shell based on the current coarse
          ceiling.
        - `cleanup()` destroys all retained idle objects and permanently retires
          the pool.
        - Subclasses define object creation and destruction behavior.

    Threading:
        - This pool intentionally does not serialize hot-path mutations with a
          pool-local lock.
        - Performance is prioritized over strict pool-internal race handling.
    """

    _DEFAULT_ENABLED: ClassVar[bool] = True
    _DEFAULT_BASELINE_IDLE: ClassVar[int] = 0
    _DEFAULT_BURST_FACTOR: ClassVar[int] = 4
    _DEFAULT_STRETCH_PERCENT: ClassVar[int] = 50
    _DEFAULT_SETTLE_TIME_SECONDS: ClassVar[float] = 300.0
    _DEFAULT_DECAY_PERCENT_PER_INTERVAL: ClassVar[int] = 10
    _DEFAULT_DECAY_INTERVAL_SECONDS: ClassVar[float] = 60.0

    __slots__ = Cleanable.__slots__ + [
        "_baseline_idle",
        "_burst_factor",
        "_enabled",
        "_borrowed_tickets",
        "_idle",
        "_max_idle",
        "_post_breach_cap",
        "_return_checkpoint",
        "_returned_tickets",
        "_target_idle",
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
        Initialize one coarse burst-pool policy state.

        Args:
            enabled:
                Whether the pool retains released objects or always destroys
                them.
            baseline_idle:
                Floor retained capacity for idle reusable shells.
            stretch_percent:
                Retained only for constructor compatibility with older callers.
                The current coarse burst model ignores this value.
            settle_time_seconds:
                Retained only for constructor compatibility with older callers.
                The current coarse burst model ignores this value.
            decay_percent_per_interval:
                Retained only for constructor compatibility with older callers.
                The current coarse burst model ignores this value.
            decay_interval_seconds:
                Retained only for constructor compatibility with older callers.
                The current coarse burst model ignores this value.
            max_idle:
                Initial retained ceiling. Defaults to `baseline_idle` when
                omitted.
            time_func:
                Retained only for constructor compatibility with older callers.
                The current coarse burst model ignores this value.

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

        self._enabled: bool = bool(enabled)
        self._baseline_idle: int = baseline_idle
        initial_cap = max(1, resolved_max_idle)
        self._burst_factor: int = self._DEFAULT_BURST_FACTOR
        self._max_idle: int = initial_cap
        self._target_idle: int = initial_cap
        self._post_breach_cap: int = initial_cap
        self._return_checkpoint: int = 0
        self._borrowed_tickets: Deque[None] = deque()
        self._returned_tickets: Deque[None] = deque()
        self._idle: Deque[_T] = deque()

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
        self._cleaned = True
        for obj in self._idle:
            self.destroy_object(obj)
        self._idle.clear()
        self._borrowed_tickets.clear()
        self._returned_tickets.clear()
        del self._idle
        del self._borrowed_tickets
        del self._returned_tickets


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
        Return the current borrowed-shell count.
        """
        return len(self._borrowed_tickets)

    @property
    def target_idle(self) -> int:
        """
        Return the current retained ceiling for idle shells.
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
        Return the current retained ceiling alias.
        """
        
        return self._max_idle

    def acquire(self, *args: Any, **kwargs: Any) -> _T:
        """
        Acquire one pooled object for use.

        Contract:
            - Reuses an idle object when available.
            - Records borrow pressure on misses before creation.
            - Expands the retained ceiling coarsely only when a miss occurs at
              the current ceiling.
            - Invokes `prepare_object(...)` on the object before returning it.

        Returns:
            _T: Prepared pooled object.
        """
        pooled_object = self._try_acquire_idle()
        if pooled_object is not None:
            return self.prepare_object(pooled_object, *args, **kwargs)
        self._record_borrow_miss()
        pooled_object = self.create_object(*args, **kwargs)
        return self.prepare_object(pooled_object, *args, **kwargs)

    def release(self, obj: _T) -> None:
        """
        Release one object back to the pool or destroy it.

        Contract:
            - Removes one borrow ticket when available.
            - Appends ordinary returned shells without cap checks until the
              coarse return threshold is reached.
            - Only when the threshold window is hit does the pool:
              - apply one shrink-step check,
              - decide whether the current returned shell still fits under the
                current ceiling.
            - Already-idle shells are never retroactively evicted when the
              ceiling drops.

        Args:
            obj: Object being returned.
        """
        if self._borrowed_tickets:
            self._borrowed_tickets.pop()
        if not self._enabled:
            self.destroy_object(obj)
            return

        self._returned_tickets.append(None)
        if len(self._returned_tickets) < self._return_check_stride:
            self._idle.append(obj)
            return

        self._returned_tickets.clear()
        self._maybe_shrink()
        if len(self._idle) < self._target_idle:
            self._idle.append(obj)
            return
        self.destroy_object(obj)

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic snapshot of the pool state.

        Returns:
            Dict[str, Any]: Current pool policy and live-count snapshot.
        """
        return {
            "enabled": self._enabled,
            "baseline_idle": self._baseline_idle,
            "target_idle": self._target_idle,
            "max_idle": self._max_idle,
            "idle_count": len(self._idle),
            "in_use_count": self.in_use_count,
            "burst_factor": self._burst_factor,
            "post_breach_cap": self._post_breach_cap,
            "return_checkpoint": self._return_checkpoint,
            "returned_tickets": len(self._returned_tickets),
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

    def _try_acquire_idle(self) -> Optional[_T]:
        """
        Reuse one idle shell when available.

        Contract:
            - Pops one idle shell from the right side of the deque.
            - Appends one borrow ticket when a shell is reused.
            - Returns `None` when no idle shell is currently retained.
        """
        if not self._enabled or not self._idle:
            return None
        self._borrowed_tickets.append(None)
        return self._idle.pop()

    def _record_borrow_miss(self) -> None:
        """
        Record one pool miss and expand the retained ceiling on breach.

        Contract:
            - Borrow pressure is tracked through `_borrowed_tickets`.
            - A breach occurs only when the miss arrives at or above the
              current retained ceiling.
            - Breach expansion is coarse and multiplicative (`x4` by default).
            - Shrink marks are recalculated from the new ceiling and floor.
        """
        if len(self._borrowed_tickets) >= self._target_idle:
            self._target_idle *= self._burst_factor
            self._max_idle = self._target_idle
            if self._baseline_idle > 0:
                self._shrink_mark = max(
                    0,
                    self._target_idle - (2 * self._baseline_idle),
                )
            else:
                self._shrink_mark = 0
            self._returned_tickets.clear()
        self._borrowed_tickets.append(None)

    def _maybe_shrink(self) -> None:
        """
        Step the retained ceiling down one floor increment when burst pressure
        has fallen through the active shrink mark.

        Contract:
            - Does nothing when the pool is disabled.
            - Does nothing while the current ceiling is already at the floor.
            - Shrinks only after borrowed pressure falls at or below the active
              shrink mark.
            - Shrinks one floor increment at a time.
        """
        if not self._enabled:
            return
        if self._baseline_idle <= 0:
            return
        if self._target_idle <= self._baseline_idle:
            return
        if len(self._borrowed_tickets) > self._shrink_mark:
            return
        self._target_idle = max(
            self._baseline_idle,
            self._target_idle - self._baseline_idle,
        )
        self._max_idle = self._target_idle
        if self._target_idle <= self._baseline_idle:
            self._shrink_mark = 0
        else:
            self._shrink_mark = max(
                0,
                self._target_idle - (2 * self._baseline_idle),
            )
