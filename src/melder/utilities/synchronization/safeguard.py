import threading
from types import TracebackType
from typing import Iterable, Optional, Sequence, Any, Literal, ClassVar
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from mypy_extensions import mypyc_attr
@mypyc_attr(native_class=True)
class SafeGuard(Cleanable):
    """
    Acquire an ordered, de-duplicated set of locks, then release in reverse order.

    Purpose:
        Provide one small lock-orchestration helper for call sites that need to
        acquire several external locks in a deterministic order without
        rewriting the same deadlock-avoidance pattern by hand.

    Contract:
        - Filters out `None` locks, de-duplicates by object identity, and sorts
          by `id(lock)` so all callers converge on the same acquisition order.
        - Works with `threading.Lock` / `threading.RLock` or any lock-like
          object exposing `acquire()` and `release()`.
        - Optional timeout applies uniformly to each acquisition attempt.
        - If any acquisition fails, already-acquired locks are released in
          reverse order before `TimeoutError` or the original exception
          propagates.
        - Re-entrant usage remains valid when the underlying lock type supports
          it, such as `RLock`.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_locks", "_acquired", "_timeout", "_one_time_use", "_cleanup_lock"]
    __deletable__: ClassVar[list[str]] = ["_locks", "_acquired", "_timeout", "_one_time_use", "_cleanup_lock"]

    def __init__(self, *locks: Any, timeout: Optional[float] = None, one_time_use: bool = True):
        """
        Build one ordered lock guard over the supplied lock objects.

        Contract:
            - Captures a deterministic acquisition order up front.
            - Stores timeout and one-time-use policy as part of the guard's own
              lifecycle.
            - Does not acquire any external locks during construction.
        """
        super().__init__()
        self._cleanup_lock: threading.RLock = threading.RLock()
        # Filter Nones, de-dupe by id, sort for global order
        uniq = {id(l): l for l in locks if l is not None}
        self._locks: list[Any] = [uniq[k] for k in sorted(uniq.keys())]
        self._acquired: list[Any] = []
        self._timeout: Optional[float]  = timeout
        self._one_time_use: bool = one_time_use

    def cleanup(self) -> None:
        """
        Release internal bookkeeping and invalidate this guard instance.

        Contract:
            - Idempotent.
            - Clears the ordered lock list and acquired-lock list.
            - Does not release external locks by itself; `__exit__()` remains
              responsible for releasing locks acquired during context use.
            - Exists to invalidate the guard object, not to substitute for a
              normal context-manager exit path.
        """
        if self._cleaned:
            return
        with self._cleanup_lock:
            if self._cleaned:
                return
            # Clear internal lists
            if self._locks is not None:
                self._locks.clear()
            if self._acquired is not None:
                self._acquired.clear()
            self._cleaned = True
            del self._locks
            del self._acquired
            del self._timeout
        del self._cleanup_lock

    def __enter__(self) -> "SafeGuard":
        """
        Acquire the ordered lock set and enter the guarded critical section.

        Contract:
            - Acquires every requested lock in deterministic order.
            - Rolls back partial acquisition on failure.
            - Returns this guard after all requested locks have been acquired.

        Returns:
            SafeGuard: This guard after all requested locks have been acquired.

        Raises:
            TimeoutError: If timed acquisition is enabled and any lock cannot be
                acquired in time.
            Exception: Re-raises any unexpected acquisition failure after
                releasing locks already acquired in this attempt.
        """
        if self._one_time_use:
            self.check_cleaned()
        try:
            if self._timeout is None:
                for lk in self._locks:
                    lk.acquire()
                    self._acquired.append(lk)
            else:
                for lk in self._locks:
                    if not lk.acquire(timeout=self._timeout):
                        raise TimeoutError("SafeGuard: timed out acquiring lock")
                    self._acquired.append(lk)
            return self
        except Exception:
            # Release anything we already grabbed
            for lk in reversed(self._acquired):
                try:
                    lk.release()
                except Exception:
                    pass
            self._acquired.clear()
            raise

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> Literal[False]:
        """
        Release acquired locks in strict reverse order.

        Contract:
            - Always releases locks in reverse acquisition order.
            - Does not suppress exceptions from the with-body.
            - Auto-cleans the guard after one-time-use contexts so it cannot be
              reused accidentally.
        """
        # Release in strict reverse order
        for lk in reversed(self._acquired):
            lk.release()
        self._acquired.clear()
        if self._one_time_use:
            self.cleanup()
        return False  # don't swallow exceptions
