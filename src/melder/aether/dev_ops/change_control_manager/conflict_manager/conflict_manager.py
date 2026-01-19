from threading import RLock
from typing import Iterable, List, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
)


class ChangeControlConflictManager(Cleanable):
    """
    Conflict detection for transaction scope overlap.

    Purpose:
        Decide whether a new request can run in parallel or must be serialized
        based on scope-key overlap with in-flight requests.
    Contract:
        - Compares scope hashes when provided; falls back to scope keys.
        - Returns request ids of conflicting in-flight requests.
    Threading:
        All state reads are guarded by an internal RLock.
    Lifecycle:
        cleanup() is idempotent and nulls internal references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the conflict manager.

        Purpose:
            Allocate the internal lock used for conflict checks.
        Contract:
            - No mutable state beyond the lock.
        Returns:
            None.
        Threading:
            Safe to publish after initialization.
        """
        super().__init__()
        self._lock: RLock = RLock()

    def cleanup(self) -> None:
        """
        Idempotent cleanup for the conflict manager.

        Purpose:
            Mark the manager as cleaned and drop the lock reference.
        Contract:
            - Safe to call multiple times.
        Returns:
            None.
        Threading:
            Acquires the internal lock while mutating state.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        self._lock = None

    def find_conflicts(
            self,
            request: ChangeControlTransactionRequest,
            in_flight: Iterable[ChangeControlTransactionRequest],
    ) -> Tuple[str, ...]:
        """
        Return in-flight request ids whose scopes overlap the supplied request.

        Purpose:
            Provide deterministic conflict detection for admission decisions.
        Contract:
            - Uses scope_hashes if present; otherwise uses scope_keys.
            - Returns an empty tuple when no conflicts are found.
        Args:
            request:
                Incoming request to evaluate.
            in_flight:
                Iterable of currently admitted requests.
        Returns:
            Tuple[str, ...]:
                Request ids that conflict with the incoming request.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while evaluating.
        """
        self.check_cleaned()
        if request is None:
            return ()
        with self._lock:
            req_keys = set(request.scope_hashes or request.scope_keys)
            if not req_keys:
                return ()
            conflicts: List[str] = []
            for active in in_flight:
                active_keys = set(active.scope_hashes or active.scope_keys)
                if req_keys.intersection(active_keys):
                    conflicts.append(active.request_id)
            return tuple(conflicts)
