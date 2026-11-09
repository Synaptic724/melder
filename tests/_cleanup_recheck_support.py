"""
Deterministic two-caller handshake for the `*_cleanup_rechecks_cleaned_inside_lock` tests.

Purpose:
    Many owned objects guard `cleanup()` with an outer `_cleaned` check, take `self._lock`, and check
    `_cleaned` again inside the lock, so a second caller that passed the outer check while the first one was
    cleaning returns without touching state the first one removed. A test proves that inner check by replacing
    the object's `_lock` with a stand-in that holds the FIRST caller inside the lock until the SECOND caller has
    passed the outer check and is about to block on the lock.

    The hand-made `_CoordinatedLock` classes those tests used decided which caller was first by reading an event
    before acquiring. When both threads read it before either set it, nobody announced the second caller; the
    first caller's one-second wait then failed inside `__enter__` with the lock held, the second thread blocked
    on that lock for good, and the test failed (GitHub #206, a macOS 3.14.1t CI run). This module orders the two
    callers explicitly instead (TASK-2026-11-08-deterministic_cleanup_recheck_handshake, GitHub #269).

Usage:
    handshake = CleanupRecheckHandshake()
    target._lock = handshake.lock
    handshake.run(target.cleanup)
    assert target.cleaned is True

    Pass `on_holder_ready` to change the object while the first caller holds the lock and the second is
    waiting - typically to mark it cleaned, as a cleanup racing in from elsewhere would.
"""
from threading import Event, Lock, RLock, Thread, get_ident
from types import TracebackType
from typing import Callable, List, Optional, Type


class CleanupRecheckLock:
    """
    Stand-in for an object's `_lock` that holds the first `cleanup()` caller until the second is about to block.

    Contract:
        - The first thread that enters is the holder: it acquires the real lock, sets `holder_entered`, waits
          until the contender announces itself through `contender_waiting`, runs `on_holder_ready` (when one was
          given) and only then returns from `__enter__`.
        - Any other thread is the contender: it sets `contender_waiting` BEFORE it blocks on the real lock, so by
          the time the holder resumes, the contender has necessarily passed the object's outer `_cleaned` check.
        - A thread entering again while it is the recorded holder re-enters the reentrant lock without
          signalling; a later entry by the contender (after the holder released) acquires normally.
        - Ordering comes from the events and from `CleanupRecheckHandshake` starting the contender only after
          `holder_entered` is set - never from timing. `WAIT_SECONDS` only bounds a broken run.
        - A failed entry never leaves the real lock held: when the contender does not arrive within
          `WAIT_SECONDS`, or `on_holder_ready` raises, the holder releases the lock before the error propagates.

    Threading:
        - The role is decided under `_state_lock`, a leaf lock taken briefly and never while waiting.
        - The real lock is an `RLock`, as the objects under test use, so a nested `with self._lock` in the holder's
          own cleanup does not deadlock.

    Lifecycle:
        - One instance serves one handshake (one holder, one contender). It owns no resource that needs cleanup.
    """

    WAIT_SECONDS: float = 10.0

    def __init__(self, on_holder_ready: Optional[Callable[[], None]] = None) -> None:
        """
        Prepare an unheld lock with no recorded holder.

        Args:
            on_holder_ready: Called by the holder, with the real lock held, once the contender is waiting; None
                leaves the object as the holder's own cleanup finds it.

        Returns:
            None.
        """
        self._lock: RLock = RLock()
        self._state_lock: Lock = Lock()
        self._holder_ident: Optional[int] = None
        self._on_holder_ready: Optional[Callable[[], None]] = on_holder_ready
        self.holder_entered: Event = Event()
        self.contender_waiting: Event = Event()

    def __enter__(self) -> CleanupRecheckLock:
        """
        Enter as the holder, the contender or a re-entering holder, in that order of first arrival.

        Returns:
            CleanupRecheckLock: This lock, as `with` binds it.

        Raises:
            AssertionError: In the holder, when the contender does not announce itself within `WAIT_SECONDS`;
                the real lock is released first.
            BaseException: Whatever `on_holder_ready` raises; the real lock is released first.
        """
        ident = get_ident()
        with self._state_lock:
            if self._holder_ident is None:
                self._holder_ident = ident
                role = "holder"
            elif self._holder_ident == ident:
                role = "reentry"
            else:
                role = "contender"
        if role == "contender":
            # Announce before blocking: the holder resumes only once this caller is past the outer check.
            self.contender_waiting.set()
        self._lock.acquire()
        if role != "holder":
            return self
        self.holder_entered.set()
        try:
            if not self.contender_waiting.wait(timeout=self.WAIT_SECONDS):
                raise AssertionError(
                    f"The second cleanup() caller did not reach the lock within {self.WAIT_SECONDS} s: "
                    "it returned before the inner check (its outer `_cleaned` check failed it) or never ran."
                )
            if self._on_holder_ready is not None:
                self._on_holder_ready()
        except BaseException:
            # Never leave the real lock held by a failed entry: `__exit__` does not run when `__enter__` raises.
            self._lock.release()
            raise
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None:
        """
        Release the real lock; never suppress the block's exception.

        Args:
            exc_type: The exception type raised in the block, or None.
            exc: The exception raised in the block, or None.
            tb: Its traceback, or None.

        Returns:
            None.
        """
        self._lock.release()


class CleanupRecheckHandshake:
    """
    Run two `cleanup()` callers through one `CleanupRecheckLock` in a fixed order and fail with a clear reason.

    Contract:
        - `lock` is the stand-in to install as the object's `_lock` before `run`.
        - `run(cleanup)` starts the holder thread, waits until it holds the lock, then starts the contender, so the
          contender always arrives second and announces itself before it blocks. Both threads are daemons, so a
          broken run cannot keep the interpreter from exiting.
        - `run` returns only when both callers finished without raising. It raises AssertionError naming what went
          wrong otherwise: the holder never took the lock, a caller is still running after `JOIN_SECONDS`, or a
          caller raised (chained from the first such error).
        - What the object looks like afterwards is the calling test's to assert.

    Threading:
        - Worker errors are collected under `_failures_lock`; the joins are bounded by `JOIN_SECONDS`.

    Lifecycle:
        - One instance serves one `run`. It owns no resource that needs cleanup; its threads have ended (or are
          reported alive) when `run` returns or raises.
    """

    JOIN_SECONDS: float = 10.0
    POLL_SECONDS: float = 0.01

    def __init__(self, on_holder_ready: Optional[Callable[[], None]] = None) -> None:
        """
        Prepare the lock and an empty failure list.

        Args:
            on_holder_ready: Passed to `CleanupRecheckLock`: called by the holder, with the lock held, once the
                contender is waiting. None leaves the object as the holder's own cleanup finds it.

        Returns:
            None.
        """
        self.lock: CleanupRecheckLock = CleanupRecheckLock(on_holder_ready=on_holder_ready)
        self._failures: List[BaseException] = []
        self._failures_lock: Lock = Lock()

    def run(self, cleanup: Callable[[], None]) -> None:
        """
        Call `cleanup` from a holder thread and then from a contender thread, and check both finished cleanly.

        Args:
            cleanup: The bound `cleanup` of the object whose `_lock` is `self.lock`.

        Returns:
            None.

        Raises:
            AssertionError: When the holder never entered the lock, a caller is still alive after the bounded
                joins, or either caller raised.
        """
        holder = Thread(target=self._call, args=(cleanup,), name="cleanup-holder", daemon=True)
        contender = Thread(target=self._call, args=(cleanup,), name="cleanup-contender", daemon=True)
        holder.start()
        self._await_holder(holder)
        contender.start()
        holder.join(timeout=self.JOIN_SECONDS)
        contender.join(timeout=self.JOIN_SECONDS)
        alive = [thread.name for thread in (holder, contender) if thread.is_alive()]
        if alive:
            raise AssertionError(f"cleanup() callers still running after {self.JOIN_SECONDS} s: {alive}.")
        self._raise_failures()

    def _await_holder(self, holder: Thread) -> None:
        """
        Wait until the holder holds the lock, failing early when it ends without entering.

        Args:
            holder: The started holder thread.

        Returns:
            None.

        Raises:
            AssertionError: When the holder ended, or `WAIT_SECONDS` passed, before it entered the lock.
        """
        waited = 0.0
        while not self.lock.holder_entered.wait(timeout=self.POLL_SECONDS):
            waited += self.POLL_SECONDS
            if not holder.is_alive() or waited >= self.lock.WAIT_SECONDS:
                holder.join(timeout=self.JOIN_SECONDS)
                self._raise_failures()
                raise AssertionError(
                    "The first cleanup() caller never entered the lock: the object's cleanup did not take its "
                    "`_lock`, or returned before it (was the object already cleaned?)."
                )

    def _call(self, cleanup: Callable[[], None]) -> None:
        """
        Run one caller, keeping any error for the test thread instead of losing it to the thread hook.

        Args:
            cleanup: The cleanup callable to invoke.

        Returns:
            None.
        """
        try:
            cleanup()
        except BaseException as error:
            with self._failures_lock:
                self._failures.append(error)

    def _raise_failures(self) -> None:
        """
        Raise one AssertionError naming every worker error, chained from the first.

        Returns:
            None.

        Raises:
            AssertionError: When at least one caller raised.
        """
        with self._failures_lock:
            failures = list(self._failures)
        if failures:
            described = "; ".join(f"{type(error).__name__}: {error}" for error in failures)
            raise AssertionError(f"cleanup() raised in {len(failures)} caller(s): {described}") from failures[0]
