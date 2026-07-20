import hashlib
from threading import RLock
from typing import Iterable, List, Set, Tuple, TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )


class ChangeControlConflictManager(Cleanable):
    """
    Conflict detector for scope overlap between change-control requests.

    This manager answers one question for admission: "Does the incoming request
    overlap any in-flight request strongly enough that it should not run in
    parallel?"

    Contract:
    - Uses scope hashes when available.
    - Derives hashes from raw scope keys when hashes are missing.
    - Also checks direct raw-key overlap when both sides provide keys.
    - Returns request ids for the in-flight requests that conflict.

    Threading:
        Detection is a pure comparison over supplied request data; it holds no
        mutable state of its own and adds no lock.

    Registration:
        MELDER KERNEL - guarded. Internal admission component reached through
        `ChangeControlManager`.

    Subsystem Context:
        The ADVISORY half of admission, distinct from the authoritative half.
        `ChangeControlEmbargoManager` owns the moded lock table and decides
        atomically what may proceed; this manager answers the softer overlap
        question against the in-flight registry.

    System Context:
        The dual detection path - hashes when available, derived hashes when
        not, plus direct raw-key comparison when both sides supply keys - is a
        robustness choice rather than redundancy. Requests arrive from several
        strategy families with differing metadata completeness, and a detector
        that understood only one representation would silently report NO
        conflict for a request that merely described its scope differently.
        False negatives are the dangerous direction: missing an overlap lets
        two structurally conflicting transactions run together, while a false
        positive merely delays one. Checking every available representation
        biases the detector toward the safe error.
        Returning request IDS rather than a boolean keeps it consistent with
        `AcquisitionDecision` - callers can name who they are waiting on, which
        is the difference between a diagnosable stall and a mysterious one.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Conflict detector for scope overlap between change-control requests. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the conflict detector.

        Contract:
        - Owns no mutable state beyond the internal lock.

        Returns:
            None.
        """
        super().__init__()
        self._lock: RLock = RLock()

    def cleanup(self) -> None:
        """
        Finalize the conflict detector.

        Contract:
        - Idempotent cleanup.
        - Drops the lock reference after the cleaned flag is set.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def find_conflicts(
            self,
            request: ChangeControlTransactionRequest,
            in_flight: Iterable[ChangeControlTransactionRequest],
    ) -> Tuple[str, ...]:
        """
        Return in-flight request ids whose scopes overlap the supplied request.

        The method is intentionally conservative: hash overlap is enough to
        report a conflict, and when both sides still have raw keys available it
        also checks direct key overlap.

        Args:
            request: Incoming request to evaluate.
            in_flight: Iterable of currently admitted requests.
        Returns:
            Tuple[str, ...]: Request ids that conflict with the incoming
            request.
        """
        
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
        Normalize request scope into a hash set for conflict comparison.

        If a request already supplies scope hashes, those win directly. If not,
        the method derives SHA256 hashes from the raw scope keys so hash-based
        and key-based requests still participate in the same overlap check.

        Args:
            scope_keys: Raw scope keys supplied by the request.
            scope_hashes: Precomputed scope hashes supplied by the request.

        Returns:
            Set[str]: Normalized hash set used by conflict detection.
        """
        
        if scope_hashes:
            return {hash_value for hash_value in scope_hashes if hash_value}
        if not scope_keys:
            return set()
        return {
            hashlib.sha256(key.encode("utf-8")).hexdigest()
            for key in scope_keys
            if key
        }
