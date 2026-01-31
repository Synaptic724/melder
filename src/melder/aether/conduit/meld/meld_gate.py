import threading

from melder.utilities.general_base.cleanable import Cleanable


class MeldGate(Cleanable):
    """
    Conduit-wide meld gate shared across a lineage tree.

    Purpose:
        Provide a deterministic, low-overhead mechanism to block or allow
        meld calls across a Conduit tree (root + lesser descendants).

    Contract:
        - `enabled` is a fast-path boolean flag used by Conduit.meld.
        - When disabled, callers block on an internal Event until re-enabled.
        - enable()/disable() are idempotent and thread-safe.
        - cleanup() unblocks any waiters and marks the gate as cleaned.

    Threading:
        - Internal RLock guards state transitions for `enabled` and the Event.
        - `enabled` is read without locking on the hot path; it is written
          under the lock in enable()/disable()/cleanup().
    """

    __slots__ = ("_lock", "enabled", "_event")

    def __init__(self, enabled: bool = True) -> None:
        """
        Public API

        Initialize a MeldGate in enabled or disabled state.

        Args:
            enabled: If True, melds pass immediately. If False, melds block
                until enable() is called.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self.enabled: bool = enabled
        self._event: threading.Event = threading.Event()
        if enabled:
            self._event.set()
        else:
            self._event.clear()

    def enable(self) -> None:
        """
        Public API

        Enable melds and release any waiting threads.

        Contract:
            - Sets enabled=True.
            - Sets the internal Event to release waiters.
            - Idempotent.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = True
            self._event.set()

    def disable(self) -> None:
        """
        Public API

        Disable melds so callers block until re-enabled.

        Contract:
            - Sets enabled=False.
            - Clears the internal Event so waiters block.
            - Idempotent.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = False
            self._event.clear()

    def wait(self) -> None:
        """
        Public API

        Block until melds are enabled.

        Contract:
            - Returns immediately if enabled.
            - Blocks on the internal Event when disabled.
        """
        self.check_cleaned()
        if self.enabled:
            return
        self._event.wait()

    def cleanup(self) -> None:
        """
        Public API

        Idempotently release any waiters and mark the gate as cleaned.

        Contract:
            - Ensures the internal Event is set to avoid deadlocks.
            - Marks the gate as cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self.enabled = True
            self._event.set()
            self._cleaned = True
