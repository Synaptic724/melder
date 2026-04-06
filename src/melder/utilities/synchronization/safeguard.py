import threading
from typing import Iterable, Optional, Sequence, Any
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

class SafeGuard(Cleanable):
    """
    Acquire an ordered, de-duplicated set of locks, then release in reverse order.

    - Orders by id(lock) so all threads take the same global order.
    - Works with threading.Lock/RLock or any lock exposing acquire()/release().
    - Optional timeout: if provided, attempts to acquire each lock with the same timeout.
      If any acquire fails, releases everything already acquired and raises TimeoutError.
    - Re-entrant friendly (RLock is naturally fine).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_locks", "_acquired", "_timeout", "_one_time_use", "_cleanup_lock"]

    def __init__(self, *locks: Any, timeout: Optional[float] = None, one_time_use: bool = True):
        super().__init__()
        self._cleanup_lock: threading.RLock = threading.RLock()
        # Filter Nones, de-dupe by id, sort for global order
        uniq = {id(l): l for l in locks if l is not None}
        self._locks: list[Any] = [uniq[k] for k in sorted(uniq.keys())]
        self._acquired: list[Any] = []
        self._timeout: Optional[float]  = timeout
        self._one_time_use: bool = one_time_use

    def cleanup(self):
        """
        Release internal bookkeeping and invalidate this guard instance.

        Contract:
            - Idempotent.
            - Clears the ordered lock list and acquired-lock list.
            - Does not release external locks by itself; `__exit__()` is still
              responsible for releasing locks acquired during context use.
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
            self._locks = None
            self._acquired = None
            self._timeout = None
            self._cleaned = True
        self._cleanup_lock = None

    def __enter__(self):
        """
        Acquire the ordered lock set and enter the guarded critical section.

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

    def __exit__(self, exc_type, exc, tb):
        """
        Release acquired locks in strict reverse order.

        Contract:
            - Always releases locks in reverse acquisition order.
            - Does not suppress exceptions from the with-body.
            - Auto-cleans the guard after one-time-use contexts.
        """
        # Release in strict reverse order
        for lk in reversed(self._acquired):
            lk.release()
        self._acquired.clear()
        if self._one_time_use:
            self.cleanup()
        return False  # don't swallow exceptions
