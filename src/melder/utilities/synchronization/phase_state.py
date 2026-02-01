from typing import Any, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class PhaseState(Cleanable):
    """
    Ephemeral per-run state shared across phase execution.

    Purpose:
        Provide a shared container for cancellation and lightweight shared data
        that can be reused across phases within the same scheduler context.

    Contract:
        - Holds a shared CancellationEvent and a mutable data bag.
        - Intended to be scoped to a single PhaseScheduler run.
        - Does not own the CancellationEvent; it only references it.

    Threading:
        - This class is **not** thread-safe.
        - Callers must provide external synchronization if multiple threads
          mutate the data bag concurrently.

    Lifecycle / Cleanup:
        - cleanup() is idempotent and clears internal references.
        - After cleanup, the instance must not be used.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_cancel_event",
        "_data",
    ]

    def __init__(
            self,
            *,
            cancel_event: Optional[CancellationEvent] = None,
            data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a PhaseState instance.

        Purpose:
            Bind an optional CancellationEvent and initialize a mutable data bag
            for phase-scoped coordination.

        Contract:
            - If data is None, a new empty dict is created.
            - The CancellationEvent is referenced but not owned.

        Args:
            cancel_event (Optional[CancellationEvent]):
                Optional cancellation signal for the current run.
            data (Optional[Dict[str, Any]]):
                Optional pre-populated data bag for phase sharing.

        Returns:
            None.
        """
        super().__init__()
        self._cancel_event: Optional[CancellationEvent] = cancel_event
        self._data: Dict[str, Any] = data if data is not None else {}

    def cleanup(self) -> None:
        """
        Clean up the PhaseState and release references.

        Purpose:
            Deterministically clear the shared data bag and drop references to
            the cancellation event.

        Contract:
            - Idempotent: safe to call multiple times.
            - After cleanup, all internal references are set to None.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._data is not None:
            self._data.clear()
        self._data = None
        self._cancel_event = None

    @property
    def cancel_event(self) -> Optional[CancellationEvent]:
        """
        Return the cancellation event shared across the current phase run.

        Returns:
            Optional[CancellationEvent]: The shared cancellation event, if any.
        Raises:
            RuntimeError: If the instance has been cleaned.
        """
        self.check_cleaned()
        return self._cancel_event

    @property
    def data(self) -> Dict[str, Any]:
        """
        Return the mutable shared data bag for phase-scoped coordination.

        Contract:
            - The returned dict is live and mutable.
            - Callers are responsible for synchronization.

        Returns:
            Dict[str, Any]: The shared data bag.
        Raises:
            RuntimeError: If the instance has been cleaned.
        """
        self.check_cleaned()
        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        """
        Fetch a value from the shared data bag.

        Args:
            key (str): Lookup key.
            default (Any): Value returned if key is missing.

        Returns:
            Any: The stored value, or default if missing.
        Raises:
            RuntimeError: If the instance has been cleaned.
        """
        self.check_cleaned()
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the shared data bag.

        Args:
            key (str): Key to set.
            value (Any): Value to store.

        Returns:
            None.
        Raises:
            RuntimeError: If the instance has been cleaned.
        """
        self.check_cleaned()
        self._data[key] = value

    def setdefault(self, key: str, default: Any) -> Any:
        """
        Insert a value only if the key is missing.

        Args:
            key (str): Lookup key.
            default (Any): Value to insert when the key is missing.

        Returns:
            Any: The existing or newly inserted value.
        Raises:
            RuntimeError: If the instance has been cleaned.
        """
        self.check_cleaned()
        return self._data.setdefault(key, default)
