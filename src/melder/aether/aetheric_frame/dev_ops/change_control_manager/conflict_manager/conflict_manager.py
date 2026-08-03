import hashlib
from threading import RLock
from typing import Iterable, List, Set, Tuple, TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )


class ChangeControlConflictManager(Cleanable):
    """
    RETIRED AT ADMISSION. Scope-overlap detector, retained deliberately, called
    by nothing.

    DO NOT READ THIS CLASS AS LIVE BEHAVIOUR. `find_conflicts` has ZERO call
    sites anywhere in `src/melder` - the only occurrence of the name is its own
    `def`. The object is still constructed per frame, occupies `__slots__` on
    both `ChangeControlManager` and `TransactionMediator`, is mandatory on the
    mediator (which raises `ValueError` when it is `None`), is exposed through a
    public property, and is threaded through two constructor signatures. All of
    that is carrying cost for a method nothing invokes.

    WHY IT WAS RETIRED (2026-06-12, scope-lock-table lane):
        Admission was rebuilt from a two-step sequence - conflict scan, then
        embargo - into ONE atomic acquisition. `ChangeControlOrchestrator`
        admission is now a single `try_acquire` of the request's merged claim
        set against `ChangeControlEmbargoManager`, which became a moded lock
        table: `ClaimMode` x / s / ix, a static compatibility matrix,
        all-or-nothing acquisition, and `(scope_key, holder_id, holder_mode)`
        blocking evidence on refusal.
        The scan did not lose an argument about being too conservative. It
        could not participate: `find_conflicts` has exactly ONE verdict -
        overlap or not - and cannot represent a shared or intent claim. The
        moded table can admit two requests that share a key while both hold
        `s`; this detector would refuse that pair. The same lane retired
        `queue_competing_root_transactions` for the same reason, replacing
        coarse global arbitration with scope-local claims and scope-local
        waiting.

    WHY IT IS RETAINED (owner ruling, 2026-08-03):
        Not for this implementation - for the CONCEPT. A conflict properly
        denotes a clash that is UNSOLVABLE and requires solutioning. The moded
        claim table produces no unsolvable states: every admission ends in
        admit, wait, or refuse-with-evidence, and all three are resolved
        outcomes. If a future conflict-based transaction family ever needs
        domain-level refusal BEYOND mode incompatibility - two requests that are
        mode-compatible but must still be refused for reasons the matrix cannot
        see - that responsibility lands here.
        Such a family would be built against `ClaimTable` / `ClaimMode`, not
        against this mode-blind hash-and-key scan. Treat the code below as a
        placeholder for the concept, not as a reusable implementation.

    TRAP - `scope_hashes` PROMISES SOMETHING NOTHING DELIVERS:
        `scope_hashes` is a PUBLIC parameter on `Spellbook.begin_transaction`
        and `Conduit.begin_transaction`. `request.scope_hashes` is READ at
        exactly two lines in the entire source tree, both inside
        `find_conflicts`, which has no callers. Supplying scope hashes declares
        no overlap and buys no isolation. Scope KEYS are the admission
        vocabulary; hashes are advisory identity evidence and carry no claims.

    Contract (INERT - describes the retired path, not live admission):
    - Uses scope hashes when available; supplied hashes win outright.
    - Derives SHA256 hashes from raw scope keys when hashes are missing.
    - Also checks direct raw-key overlap when both sides provide keys.
    - Returns request ids for the in-flight requests that conflict.

    Threading:
        Detection is a pure comparison over supplied request data; it holds no
        mutable state of its own beyond the lock taken during comparison.

    Registration:
        MELDER KERNEL - guarded. Internal component reached through
        `ChangeControlManager`. No longer part of the admission path.

    HISTORICAL DESIGN REASONING (preserved; applied when the path was live):
        The dual detection path - hashes when available, derived hashes when
        not, plus direct raw-key comparison when both sides supply keys - was a
        robustness choice rather than redundancy. Requests arrive from several
        strategy families with differing metadata completeness, and a detector
        that understood only one representation would silently report NO
        conflict for a request that merely described its scope differently.
        False negatives were the dangerous direction: missing an overlap lets
        two structurally conflicting transactions run together, while a false
        positive merely delays one. Checking every available representation
        biased the detector toward the safe error.
        Returning request IDS rather than a boolean kept it consistent with
        `AcquisitionDecision` - callers can name who they are waiting on, which
        is the difference between a diagnosable stall and a mysterious one.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. RETIRED scope-overlap detector - `find_conflicts` has
        zero call sites and is NOT part of admission. Admission is one atomic
        moded acquisition against ChangeControlEmbargoManager. Retained as a
        placeholder for a future conflict-based transaction family, not as a
        live path. Do not drive it and do not describe it as active behaviour.
    """
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
