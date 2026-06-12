import time
from dataclasses import dataclass
from enum import StrEnum
from threading import Condition, RLock
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )


class ClaimMode(StrEnum):
    """
    Claim modes for scope-key acquisition.

    Purpose:
        Classify how strongly one transaction claims one scope key so the
        admission gate can admit share-compatible work in parallel while
        serializing true structural overlap.

    Contract:
        - Values are stable because they travel in request payloads and logs.
        - `EXCLUSIVE` ("x") is the default and matches pre-mode semantics: no
          other claim of any mode may coexist on the same scope key.
        - `SHARED` ("s") permits coexistence with other `SHARED` claims only.
        - `INTENT` ("ix") is the parent-scope marker for hierarchical claims
          and permits coexistence with other `INTENT` claims only.

    Threading:
        Stateless enum; safe to share across threads.
    """
    __melder_internal__ = _mrg.sentinel
    EXCLUSIVE = "x"
    SHARED = "s"
    INTENT = "ix"


@dataclass(frozen=True)
class ChangeControlEmbargoRecord:
    """
    Immutable record describing one claimed scope key.

    Purpose:
        Capture one request-owned scope claim in a form that admission,
        diagnostics, and advisory tooling can share safely.

    Contract:
        - Each record ties one normalized scope key to the request that holds
          the claim and the mode it is held in.
        - `reason_tag` carries the lightweight operational reason associated
          with the claim, such as the admitted transaction type.
        - Records are immutable and may be copied freely across threads or
          tooling boundaries.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    scope_key: str
    reason_tag: str
    owner_request_id: str
    created_at: float
    mode: ClaimMode = ClaimMode.EXCLUSIVE


@dataclass(frozen=True)
class AcquisitionDecision:
    """
    Immutable outcome of one all-or-nothing scope acquisition attempt.

    Purpose:
        Report whether a claim set was granted and, on failure, exactly which
        scope keys blocked it and who holds them.

    Contract:
        - `acquired=True` means every requested claim was granted atomically.
        - `blocking` holds `(scope_key, holder_request_id, holder_mode)`
          tuples and is empty on success.
        - Instances are immutable and safe to share across threads.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    acquired: bool
    blocking: Tuple[Tuple[str, str, str], ...] = ()


class ChangeControlEmbargoManager(Cleanable):
    """
    Moded scope-key lock table for transaction admission.

    Purpose:
        Own the single admission gate for change-control transactions: an
        atomic, all-or-nothing acquisition surface over normalized scope keys
        with per-claim modes, plus scope-local waiting so blocked requests can
        admit when conflicting claims release.

    Contract:
        - Claims are owned by request id, not by standalone lifecycle objects.
        - Acquisition is all-or-nothing under the manager lock; a failed
          attempt acquires nothing and reports blocking evidence.
        - Compatibility is decided only by the static mode matrix
          (`_modes_compatible`); an owner's own claims never block it.
        - Scope and owner indexes stay in sync.
        - Commit/abort flows release claims through the owner-request path and
          wake all waiters.
        - Legacy binary-embargo surfaces (`open_embargo`, `find_embargoes`,
          `apply_implicit_embargoes`) remain and operate in
          `ClaimMode.EXCLUSIVE` for compatibility.

    Threading:
        One `RLock` guards all state; one `Condition` on that lock wakes
        blocked acquirers on every release and on cleanup. Waiters re-evaluate
        their full claim set per wake, so spurious wakeups are safe.

    Lifecycle:
        `cleanup()` marks the manager cleaned and notifies all waiters before
        dropping state so blocked threads fail fast instead of hanging.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_condition",
        "_embargoes_by_scope",
        "_embargoes_by_owner",
    ]

    def __init__(self) -> None:
        """
        Initialize the lock table.

        Contract:
        - Starts with empty scope and owner indexes.
        - The wait condition shares the manager lock so release notifications
          and acquisition checks serialize correctly.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._condition: Condition = Condition(self._lock)
        self._embargoes_by_scope: Dict[str, List[ChangeControlEmbargoRecord]] = {}
        self._embargoes_by_owner: Dict[str, Set[str]] = {}

    def cleanup(self) -> None:
        """
        Finalize the lock table.

        Contract:
        - Idempotent cleanup.
        - Notifies all waiters after marking cleaned so blocked acquirers
          observe the cleaned state and raise instead of hanging.
        - Clears both claim indexes before dropping owned references.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._embargoes_by_scope is not None:
                self._embargoes_by_scope.clear()
            if self._embargoes_by_owner is not None:
                self._embargoes_by_owner.clear()

            del self._embargoes_by_scope
            del self._embargoes_by_owner
        # Notify under the condition's own context so waiters wake even if
        # `_lock` was rebound after construction (test doubles); the condition
        # always owns the lock it was built with.
        with self._condition:
            self._condition.notify_all()
        del self._condition
        del self._lock

    @staticmethod
    def _modes_compatible(held: ClaimMode, requested: ClaimMode) -> bool:
        """
        Return whether a requested claim may coexist with one held claim.

        Contract (static matrix, held vs requested):
        - `EXCLUSIVE` is incompatible with everything.
        - `SHARED` is compatible only with `SHARED`.
        - `INTENT` is compatible only with `INTENT`.

        Args:
            held: Mode of the claim already held by another owner.
            requested: Mode of the incoming claim.

        Returns:
            bool: True when both claims may be held concurrently.
        """
        if held is ClaimMode.EXCLUSIVE or requested is ClaimMode.EXCLUSIVE:
            return False
        return held is requested

    @staticmethod
    def _normalize_claims(
            claims: Iterable[Tuple[str, "ClaimMode | str"]],
    ) -> Dict[str, ClaimMode]:
        """
        Normalize one claim iterable into a scope-key -> mode map.

        Contract:
        - Empty scope keys are dropped.
        - String modes are converted through `ClaimMode`; invalid values raise.
        - Duplicate keys keep the strongest mode (`EXCLUSIVE` > `SHARED` /
          `INTENT`), so callers cannot accidentally weaken a claim by listing
          the key twice.

        Args:
            claims: Iterable of `(scope_key, mode)` pairs.

        Returns:
            Dict[str, ClaimMode]: Normalized claim map.

        Raises:
            ValueError: If a mode value is not a valid `ClaimMode`.
        """
        normalized: Dict[str, ClaimMode] = {}
        for scope_key, raw_mode in claims:
            if not scope_key:
                continue
            mode = raw_mode if isinstance(raw_mode, ClaimMode) else ClaimMode(raw_mode)
            existing = normalized.get(scope_key)
            if existing is None or mode is ClaimMode.EXCLUSIVE:
                normalized[scope_key] = mode
        return normalized

    def try_acquire(
            self,
            *,
            owner_request_id: str,
            claims: Iterable[Tuple[str, "ClaimMode | str"]],
            reason_tag: str,
    ) -> AcquisitionDecision:
        """
        Attempt one atomic, all-or-nothing acquisition of a claim set.

        Contract:
        - On success, every requested claim is recorded and indexed before the
          lock releases.
        - On failure, nothing is recorded and the decision carries one
          `(scope_key, holder_request_id, holder_mode)` tuple per blocking
          claim.
        - The owner's own held claims never block it; re-requesting a held key
          at the same or weaker mode is a no-op, and a `SHARED`->`EXCLUSIVE`
          upgrade is granted only when the owner is the sole holder of that
          key.
        - An empty claim set acquires immediately.

        Args:
            owner_request_id: Request id that will own the claims.
            claims: Iterable of `(scope_key, mode)` pairs.
            reason_tag: Short diagnostic reason recorded on new claims.

        Returns:
            AcquisitionDecision: Grant result with blocking evidence on
            failure.

        Raises:
            ValueError: If `owner_request_id` or `reason_tag` is empty, or a
                mode value is invalid.
            RuntimeError: If the manager has been cleaned.
        """
        self.check_cleaned()
        if not owner_request_id or not reason_tag:
            raise ValueError("owner_request_id and reason_tag are required")
        normalized = self._normalize_claims(claims)
        if not normalized:
            return AcquisitionDecision(acquired=True)
        created_at = time.time()
        with self._lock:
            blocking: List[Tuple[str, str, str]] = []
            for scope_key, mode in normalized.items():
                for record in self._embargoes_by_scope.get(scope_key, ()):
                    if record.owner_request_id == owner_request_id:
                        continue
                    if not self._modes_compatible(record.mode, mode):
                        blocking.append(
                            (scope_key, record.owner_request_id, record.mode.value)
                        )
            if blocking:
                return AcquisitionDecision(
                    acquired=False,
                    blocking=tuple(blocking),
                )
            for scope_key, mode in normalized.items():
                if self._owner_holds_at_least(owner_request_id, scope_key, mode):
                    continue
                record = ChangeControlEmbargoRecord(
                    scope_key=scope_key,
                    reason_tag=reason_tag,
                    owner_request_id=owner_request_id,
                    created_at=created_at,
                    mode=mode,
                )
                self._embargoes_by_scope.setdefault(scope_key, []).append(record)
                self._embargoes_by_owner.setdefault(owner_request_id, set()).add(
                    scope_key
                )
            return AcquisitionDecision(acquired=True)

    def _owner_holds_at_least(
            self,
            owner_request_id: str,
            scope_key: str,
            mode: ClaimMode,
    ) -> bool:
        """
        Internal

        Return whether the owner already holds the key at the requested
        strength or stronger.

        Caller contract:
            The manager lock must already be held.

        Args:
            owner_request_id: Owner being checked.
            scope_key: Scope key being requested.
            mode: Requested mode.

        Returns:
            bool: True when no new record is needed for this claim.
        """
        for record in self._embargoes_by_scope.get(scope_key, ()):
            if record.owner_request_id != owner_request_id:
                continue
            if record.mode is ClaimMode.EXCLUSIVE or record.mode is mode:
                return True
        return False

    def wait_for_release(self, timeout: float) -> bool:
        """
        Block the calling thread until any claim releases or timeout expires.

        Purpose:
            Provide the scope-local pending primitive: blocked acquirers wait
            here between acquisition attempts and are woken by every owner
            release and by cleanup.

        Contract:
            - Returns True when notified before the timeout, False on timeout.
            - Callers must re-attempt their full acquisition after waking;
              a wake is a hint, not a grant.

        Args:
            timeout: Maximum seconds to wait for one notification.

        Returns:
            bool: True when woken by a release, False on timeout.

        Raises:
            RuntimeError: If the manager has been cleaned (including while
                waiting).
        """
        self.check_cleaned()
        # Wait under the condition's own context so the wait is always paired
        # with the lock the condition owns, independent of `_lock` rebinding.
        with self._condition:
            notified = self._condition.wait(timeout=timeout)
        self.check_cleaned()
        return notified

    def release_owner(self, owner_request_id: str) -> None:
        """
        Release every claim held by the supplied request id and wake waiters.

        Contract:
        - Idempotent; unknown owners no-op (but still notify waiters so the
          release path is uniformly safe to call from commit and abort).
        - Both claim indexes are updated before notification.

        Args:
            owner_request_id: Request id whose claims should be released.
        """
        if not owner_request_id:
            return
        with self._lock:
            scope_keys = self._embargoes_by_owner.pop(owner_request_id, set())
            for scope_key in scope_keys:
                records = self._embargoes_by_scope.get(scope_key, [])
                records = [
                    record
                    for record in records
                    if record.owner_request_id != owner_request_id
                ]
                if records:
                    self._embargoes_by_scope[scope_key] = records
                elif scope_key in self._embargoes_by_scope:
                    del self._embargoes_by_scope[scope_key]
        # Notify under the condition's own context (see cleanup note); waking
        # after the mutation is safe because waiters re-attempt their full
        # acquisition on every wake.
        with self._condition:
            self._condition.notify_all()

    def open_embargo(
            self,
            *,
            scope_keys: Iterable[str],
            reason_tag: str,
            owner_request_id: str,
            mode: ClaimMode = ClaimMode.EXCLUSIVE,
    ) -> None:
        """
        Unconditionally record claims for the supplied scope keys.

        Purpose:
            Legacy/compatibility write path that records claims without the
            all-or-nothing compatibility check. New admission flows should use
            `try_acquire(...)`.

        Contract:
        - Multiple claims may accumulate for the same scope when different
          in-flight requests record it independently.
        - Defaults to `EXCLUSIVE` to preserve pre-mode semantics.

        Args:
            scope_keys: Scope keys to claim.
            reason_tag: Short diagnostic reason for the claims.
            owner_request_id: Request id that owns the claims.
            mode: Claim mode recorded on each new record.

        Raises:
            ValueError: If `owner_request_id` or `reason_tag` is empty.
        """
        if not owner_request_id or not reason_tag:
            raise ValueError("owner_request_id and reason_tag are required")
        created_at = time.time()
        with self._lock:
            for scope_key in scope_keys:
                if not scope_key:
                    continue
                record = ChangeControlEmbargoRecord(
                    scope_key=scope_key,
                    reason_tag=reason_tag,
                    owner_request_id=owner_request_id,
                    created_at=created_at,
                    mode=mode,
                )
                self._embargoes_by_scope.setdefault(scope_key, []).append(record)
                self._embargoes_by_owner.setdefault(owner_request_id, set()).add(scope_key)

    def extend_embargoes(
            self,
            *,
            owner_request_id: str,
            scope_keys: Iterable[str],
            reason_tag: str,
    ) -> None:
        """
        Extend claims for an existing request with additional scope keys.

        This is the staged-update path for requests that discover new scope
        after admission. Existing claims for the same owner are preserved;
        only genuinely new scope keys are added. Extensions are recorded
        unconditionally in `EXCLUSIVE` mode (pre-mode semantic preserved);
        conflicts created by extension surface to later acquisitions, not to
        the extending owner.

        Args:
            owner_request_id: Request id that owns the claims.
            scope_keys: Additional scope keys to claim.
            reason_tag: Diagnostic reason tag for the new records.

        Raises:
            ValueError: If `owner_request_id` or `reason_tag` is empty.
        """
        if not owner_request_id or not reason_tag:
            raise ValueError("owner_request_id and reason_tag are required")
        created_at = time.time()
        with self._lock:
            existing = set(self._embargoes_by_owner.get(owner_request_id, set()))
            for scope_key in scope_keys:
                if not scope_key or scope_key in existing:
                    continue
                record = ChangeControlEmbargoRecord(
                    scope_key=scope_key,
                    reason_tag=reason_tag,
                    owner_request_id=owner_request_id,
                    created_at=created_at,
                    mode=ClaimMode.EXCLUSIVE,
                )
                self._embargoes_by_scope.setdefault(scope_key, []).append(record)
                self._embargoes_by_owner.setdefault(owner_request_id, set()).add(scope_key)
                existing.add(scope_key)

    def close_embargo(self, owner_request_id: str) -> None:
        """
        Close all claims owned by the supplied request id.

        This is the normal release path after commit or abort and delegates to
        `release_owner(...)`, which also wakes blocked acquirers.

        Args:
            owner_request_id: Request id whose claims should be released.
        """
        self.release_owner(owner_request_id)

    def find_embargoes(self, scope_keys: Iterable[str]) -> Tuple[str, ...]:
        """
        Return scope keys that currently carry any claim.

        This is the legacy binary query surface; it does not consider modes.
        Admission flows should prefer `try_acquire(...)`, which reports
        blocking evidence with holder identity and mode.

        Args:
            scope_keys:
                Scope keys to check for claims.
        Returns:
            Tuple[str, ...]:
                Scope keys that carry at least one claim.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while checking registries.
        """
        blocked: List[str] = []
        with self._lock:
            for scope_key in scope_keys:
                if scope_key in self._embargoes_by_scope:
                    blocked.append(scope_key)
        return tuple(blocked)

    def list_advisory_hints(
            self,
            scope_keys: Iterable[str],
    ) -> Tuple[ChangeControlEmbargoRecord, ...]:
        """
        Return advisory claim records for the supplied scope keys.

        Purpose:
            Provide soft-lock hints that agents can honor before mutation,
            including holder identity, mode, reason, and held-since time.
        Contract:
            - Returns a tuple of claim records (may be empty).
            - Does not block or mutate state.
        Args:
            scope_keys:
                Scope keys to check for advisory hints.
        Returns:
            Tuple[ChangeControlEmbargoRecord, ...]:
                Claim records covering the supplied scopes.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while copying records.
        """
        hints: List[ChangeControlEmbargoRecord] = []
        with self._lock:
            for scope_key in scope_keys:
                records = self._embargoes_by_scope.get(scope_key)
                if not records:
                    continue
                hints.extend(records)
        return tuple(hints)

    def collect_scope_keys(
            self,
            request: "ChangeControlTransactionRequest",
    ) -> Tuple[str, ...]:
        """
        Build a scope-key set for acquisition from a request payload.

        Purpose:
            Normalize scope keys used for claim derivation so admission uses
            consistent scope comparisons.
        Contract:
            - Includes request.scope_keys.
            - Adds derived spellbook/conduit/binding/contract scopes when present.
        Args:
            request:
                Transaction request to normalize.
        Returns:
            Tuple[str, ...]:
                Normalized scope keys for acquisition.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        return self._collect_scope_keys_from_fields(
            scope_keys=request.scope_keys,
            spellbook_id=request.spellbook_id,
            conduit_ids=request.conduit_ids,
            binding_keys=request.binding_keys,
            contract_keys=request.contract_keys,
        )

    def collect_scope_keys_from_staged(
            self,
            staged: "ChangeControlStagedMutation",
    ) -> Tuple[str, ...]:
        """
        Build scope keys for acquisition from staged mutation metadata.

        Purpose:
            Normalize scope keys when staged metadata updates occur after admission.
        Contract:
            - Returns an empty tuple if staged is None.
        Args:
            staged:
                Staged mutation to normalize.
        Returns:
            Tuple[str, ...]:
                Normalized scope keys for acquisition.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        if staged is None:
            return ()
        return self._collect_scope_keys_from_fields(
            scope_keys=staged.scope_keys,
            spellbook_id=staged.spellbook_id,
            conduit_ids=staged.conduit_ids,
            binding_keys=staged.binding_keys,
            contract_keys=staged.contract_keys,
        )

    def _collect_scope_keys_from_fields(
            self,
            *,
            scope_keys: Iterable[str],
            spellbook_id: Optional[str],
            conduit_ids: Iterable[str],
            binding_keys: Iterable[Tuple[str, str]],
            contract_keys: Iterable[Tuple[str, str, str]],
    ) -> Tuple[str, ...]:
        """
        Internal

        Build normalized scope keys from field values.

        Purpose:
            Provide a shared scope-key derivation for requests and staged updates.
        Contract:
            - Returns sorted, de-duplicated scope keys.
        Args:
            scope_keys:
                Optional explicit scope keys.
            spellbook_id:
                Optional spellbook id to normalize.
            conduit_ids:
                Optional conduit ids to normalize.
            binding_keys:
                Optional binding keys to normalize.
            contract_keys:
                Optional contract keys to normalize.
        Returns:
            Tuple[str, ...]:
                Normalized scope keys for acquisition.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        scope_set: Set[str] = set()
        if scope_keys:
            scope_set.update(key for key in scope_keys if key)
        if spellbook_id:
            scope_set.add(f"scope:spellbook:{spellbook_id}")
        if conduit_ids:
            for conduit_id in conduit_ids:
                if conduit_id:
                    scope_set.add(f"scope:conduit:{conduit_id}")
        if binding_keys:
            for frame_key, binding_key in binding_keys:
                if frame_key and binding_key:
                    scope_set.add(f"binding:{frame_key}:{binding_key}")
        if contract_keys:
            for frame_key, binding_key, peer_conduit_id in contract_keys:
                if frame_key and binding_key and peer_conduit_id:
                    scope_set.add(f"contract:{frame_key}:{binding_key}:{peer_conduit_id}")
        return tuple(sorted(scope_set))

    def collect_scope_claims(
            self,
            request: "ChangeControlTransactionRequest",
    ) -> Tuple[Tuple[str, ClaimMode], ...]:
        """
        Build the full moded claim set for one request.

        Purpose:
            Merge the request's explicit `scope_claims` with the derived scope
            keys so admission acquires every relevant key exactly once.

        Contract:
            - Derived keys without an explicit mode default to `EXCLUSIVE`.
            - Explicit `scope_claims` modes win for their keys.
            - Invalid explicit modes raise `ValueError`.

        Args:
            request:
                Transaction request to normalize.

        Returns:
            Tuple[Tuple[str, ClaimMode], ...]:
                Sorted, de-duplicated `(scope_key, mode)` claim pairs.
        """
        explicit: Dict[str, ClaimMode] = {}
        for scope_key, raw_mode in getattr(request, "scope_claims", ()) or ():
            if not scope_key:
                continue
            explicit[scope_key] = (
                raw_mode if isinstance(raw_mode, ClaimMode) else ClaimMode(raw_mode)
            )
        merged: Dict[str, ClaimMode] = {}
        for scope_key in self.collect_scope_keys(request):
            merged[scope_key] = explicit.get(scope_key, ClaimMode.EXCLUSIVE)
        for scope_key, mode in explicit.items():
            merged.setdefault(scope_key, mode)
        return tuple(sorted(merged.items()))

    def apply_implicit_embargoes(self, request: "ChangeControlTransactionRequest") -> None:
        """
        Record claims for the admitted request's derived scope keys.

        Purpose:
            Legacy/compatibility hook retained for callers that admit outside
            `try_acquire(...)`. The orchestrator acquisition path supersedes
            this; acquisition itself records the claims.
        Contract:
            - Records claims for derived scope keys tied to the request.
        Args:
            request:
                Admitted request for which to record claims.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while updating registries.
        """
        scope_keys = self.collect_scope_keys(request)
        if not scope_keys:
            return
        self.open_embargo(
            scope_keys=scope_keys,
            reason_tag=(
                request.request_type.value
                if hasattr(request.request_type, "value")
                else str(request.request_type)
            ),
            owner_request_id=request.request_id,
        )

    def release_implicit_embargoes(self, request: "ChangeControlTransactionRequest") -> None:
        """
        Release claims held by the supplied request.

        Purpose:
            Release every claim owned by the request after commit or abort.
        Contract:
            - Delegates to `release_owner(...)`, which also wakes blocked
              acquirers; this is not a read-only diagnostic helper.
        Args:
            request:
                Admitted request whose claims should be released.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Delegates to `release_owner(...)`, which mutates registry state
            under the manager lock.
        """
        self.release_owner(request.request_id)

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot for lock-table state.

        Purpose:
            Provide a concise view of active claimed scopes.
        Contract:
            - Returns snapshots only; no internal state is exposed for mutation.
        Returns:
            Dict[str, Any]:
                Diagnostic metadata for tooling.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while copying.
        """
        with self._lock:
            return {
                "embargoed_scopes": list(self._embargoes_by_scope.keys()),
                "embargo_count": sum(len(v) for v in self._embargoes_by_scope.values()),
            }
