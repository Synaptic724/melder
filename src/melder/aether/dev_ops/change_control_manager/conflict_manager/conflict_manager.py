import hashlib
from threading import RLock
from typing import Iterable, List, Set, Tuple

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
        - Compares scope hashes when available; derives hashes from keys when missing.
        - Falls back to raw scope keys when both requests supply keys.
        - Returns request ids of conflicting in-flight requests.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
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
            - Uses scope_hashes when available; otherwise derives from scope_keys.
            - Also checks raw scope_keys when both requests provide keys.
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
            req_hashes = self._normalize_hashes(request.scope_keys, request.scope_hashes)
            req_keys = set(request.scope_keys)
            if not req_hashes and not req_keys:
                return ()
            conflicts: List[str] = []
            for active in in_flight:
                active_hashes = self._normalize_hashes(active.scope_keys, active.scope_hashes)
                active_keys = set(active.scope_keys)
                if req_hashes and active_hashes and req_hashes.intersection(active_hashes):
                    conflicts.append(active.request_id)
                    continue
                if req_keys and active_keys and req_keys.intersection(active_keys):
                    conflicts.append(active.request_id)
            return tuple(conflicts)

    def _normalize_hashes(
            self,
            scope_keys: Iterable[str],
            scope_hashes: Iterable[str],
    ) -> Set[str]:
        """
        Internal

        Normalize scope hashes for conflict comparison.

        Purpose:
            Ensure hash-only and key-only requests still overlap during
            conflict checks by deriving hashes when needed.
        Contract:
            - Returns provided scope_hashes when present.
            - Derives SHA256 hashes from scope_keys when hashes are empty.
        Args:
            scope_keys:
                Raw scope keys provided by the request.
            scope_hashes:
                Precomputed scope hashes provided by the request.
        Returns:
            Set[str]:
                Normalized hash set for conflict comparison.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if scope_hashes:
            return {hash_value for hash_value in scope_hashes if hash_value}
        if not scope_keys:
            return set()
        return {
            hashlib.sha256(key.encode("utf-8")).hexdigest()
            for key in scope_keys
            if key
        }
