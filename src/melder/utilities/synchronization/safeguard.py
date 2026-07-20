import threading
from types import TracebackType
from typing import Iterable, Optional, Sequence, Any, Literal, ClassVar
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable


class SafeGuard(Cleanable):
    """
    Acquire an ordered, de-duplicated set of locks, then release in reverse order.

    Purpose:
        Provide one small lock-orchestration helper for call sites that need to
        acquire several external locks in a deterministic order without
        rewriting the same deadlock-avoidance pattern by hand.

    Responsibilities:
        - Normalize a lock set: drop `None`, de-duplicate by identity, order it.
        - Acquire every lock in that order, rolling back cleanly on failure.
        - Release in strict reverse order on exit.
        - Invalidate itself after a one-time-use context so it cannot be reused.

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

    How The Ordering Actually Works:
        Acquisition order is `sorted(id(lock))`, NOT argument order. That is the
        entire deadlock-avoidance mechanism: two call sites passing the same two
        locks in opposite argument order still acquire them in the same real
        order, so they cannot deadlock against each other.

        The guarantee holds over CONCURRENTLY LIVE locks, which is the case that
        matters - distinct live objects have distinct ids. It is NOT a stable
        ordering across process runs, and it is not a priority: `id()` is an
        address, so the order is arbitrary but consistent. Do not depend on
        which lock is taken first, only on the fact that everyone agrees.

    Timeout Semantics (read before setting one):
        The timeout is PER LOCK, not for the whole acquisition. Guarding four
        locks with `timeout=1.0` can block for four seconds before raising.
        Budget accordingly; there is no overall deadline.

    Owned State:
        - `_locks`: the normalized, ordered lock list.
        - `_acquired`: locks currently held by this guard, in acquisition order.
        - `_timeout`: per-acquisition timeout, or None for untimed blocking.
        - `_one_time_use`: whether `__exit__` self-cleans.
        - `_cleanup_lock`: guards this object's own teardown, not the guarded
          locks.

    Threading:
        The guard itself is not designed to be shared across threads - it holds
        per-context acquisition state in `_acquired`. Give each thread its own
        `SafeGuard`. What IS shared safely is the ordering RULE, which is what
        makes independent guards in different threads compatible.

        The rollback path in `__enter__` swallows exceptions from release calls
        deliberately: a failure while unwinding must not mask the acquisition
        failure that caused the unwind. `__exit__` does NOT swallow, because a
        failed release on the happy path is a real defect worth surfacing.

    Lifecycle / Cleanup:
        `one_time_use` defaults to True, so a guard is SINGLE USE: `__exit__`
        calls `cleanup()` and any second `__enter__` raises through
        `check_cleaned()`. Construct one per critical section.

        HAZARD: `cleanup()` deliberately does not release external locks - it
        only clears bookkeeping and invalidates the guard. Calling it directly
        while locks are held leaks them permanently. Let `__exit__` do the
        releasing; treat `cleanup()` as invalidation only.

    Registration:
        MELDER KERNEL - guarded. Melder owns lock-orchestration policy, so this
        cannot be registered as a spell. It IS intended for direct user import
        and use: guarding and exporting are orthogonal, and this is a case where
        a user calls the class directly but must never ask Melder to inject one.

    Subsystem Context:
        Part of `utilities/synchronization/`, the concurrency primitive family.
        Where the gates (`LoadGate`, `CreationGate`) answer "may this proceed"
        and the scheduler answers "run these in phases", `SafeGuard` answers the
        narrower question "how do I take several locks without deadlocking". It
        owns no policy about WHICH locks matter; callers decide that.

    System Context:
        Used wherever the runtime must hold two independent lock domains at
        once - most visibly `ConduitWard` contract creation, which locks both
        wards, and ownership transfer, which locks source and target conduits
        while flipping registries. Those are exactly the paths where two threads
        could approach the same pair from opposite ends, which is why the
        ordering rule exists rather than ad-hoc nested `with` statements.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Deadlock-safe multi-lock acquisition. Use as a context "
        "manager over several locks: SafeGuard(a, b, c) acquires them in a "
        "globally consistent order and releases in reverse. Single-use by "
        "default. Import and call directly; cannot be bound as a spell."
    )
    __slots__ = Cleanable.__slots__ + ["_locks", "_acquired", "_timeout", "_one_time_use", "_cleanup_lock"]

    def __init__(self, *locks: Any, timeout: Optional[float] = None, one_time_use: bool = True):
        """
        Build one ordered lock guard over the supplied lock objects.

        Contract:
            - Captures a deterministic acquisition order up front.
            - Stores timeout and one-time-use policy as part of the guard's own
              lifecycle.
            - Does not acquire any external locks during construction.

        Returns:
            None.

        Args:
            locks:
                Locks to acquire together. SafeGuard orders them deterministically
                so two SafeGuards over the same locks cannot deadlock against each other.
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

        Returns:
            None.
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
