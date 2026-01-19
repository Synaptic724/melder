import time
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Iterable, List, Set, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
)


@dataclass(frozen=True)
class ChangeControlEmbargoRecord:
    """
    Internal record for an embargoed scope key.

    Purpose:
        Capture embargo ownership and timing metadata for a scope key.
    Contract:
        - Instances are immutable.
        - owner_request_id ties the embargo to a specific transaction.
    Args:
        scope_key:
            Scope key under embargo.
        reason_tag:
            Short reason code for diagnostics.
        owner_request_id:
            Request id that owns the embargo.
        created_at:
            Unix timestamp (seconds) when the embargo was created.
    Returns:
        None.
    Raises:
        None.
    Threading:
        Safe to share across threads because instances are immutable.
    Lifecycle:
        Immutable; no cleanup required.
    """
    __melder_internal__ = _mrg.sentinel
    scope_key: str
    reason_tag: str
    owner_request_id: str
    created_at: float


class ChangeControlEmbargoManager(Cleanable):
    """
    Embargo registry for blocking or hinting against requests by scope key.

    Purpose:
        Provide scope-based gating so conflicting requests can be rejected
        while a change transaction is active.
    Contract:
        - Embargoes are internal, transaction-driven state (not standalone
          transactions).
        - Embargoes are released on commit/abort of their owning request.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Threading:
        All state mutations are guarded by an internal RLock.
    Lifecycle:
        cleanup() is idempotent and nulls internal references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_embargoes_by_scope",
        "_embargoes_by_owner",
    ]

    def __init__(self) -> None:
        """
        Initialize the embargo manager.

        Purpose:
            Create empty embargo registries for scope and owner tracking.
        Contract:
            - Registries start empty.
        Returns:
            None.
        Threading:
            Safe to publish after initialization.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._embargoes_by_scope: Dict[str, List[ChangeControlEmbargoRecord]] = {}
        self._embargoes_by_owner: Dict[str, Set[str]] = {}

    def cleanup(self) -> None:
        """
        Idempotent cleanup for embargo registries.

        Purpose:
            Release registries and lock references for GC safety.
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
            if self._embargoes_by_scope is not None:
                self._embargoes_by_scope.clear()
                self._embargoes_by_scope = None
            if self._embargoes_by_owner is not None:
                self._embargoes_by_owner.clear()
                self._embargoes_by_owner = None
        self._lock = None

    def open_embargo(
            self,
            *,
            scope_keys: Iterable[str],
            reason_tag: str,
            owner_request_id: str,
    ) -> None:
        """
        Open embargoes for the supplied scope keys.

        Purpose:
            Block conflicting requests while a transaction is active.
        Contract:
            - Each scope key becomes embargoed under the owner_request_id.
            - Multiple embargo records can exist per scope key.
        Args:
            scope_keys:
                Scope keys to embargo.
            reason_tag:
                Short reason string for diagnostics.
            owner_request_id:
                Request id that owns the embargo.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If owner_request_id or reason_tag is empty.
        Threading:
            Acquires the internal lock while updating registries.
        """
        self.check_cleaned()
        if not owner_request_id or not reason_tag:
            raise ValueError("owner_request_id and reason_tag are required")
        created_at = time.time()
        with self._lock:
            for scope_key in scope_keys:
                record = ChangeControlEmbargoRecord(
                    scope_key=scope_key,
                    reason_tag=reason_tag,
                    owner_request_id=owner_request_id,
                    created_at=created_at,
                )
                self._embargoes_by_scope.setdefault(scope_key, []).append(record)
                self._embargoes_by_owner.setdefault(owner_request_id, set()).add(scope_key)

    def close_embargo(self, owner_request_id: str) -> None:
        """
        Close all embargoes owned by the supplied request id.

        Purpose:
            Release embargoes when a transaction commits or aborts.
        Contract:
            - No error if the owner has no active embargoes.
        Args:
            owner_request_id:
                Request id that owns the embargoes.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while updating registries.
        """
        self.check_cleaned()
        if not owner_request_id:
            return
        with self._lock:
            scope_keys = self._embargoes_by_owner.pop(owner_request_id, set())
            for scope_key in scope_keys:
                records = self._embargoes_by_scope.get(scope_key, [])
                records = [rec for rec in records if rec.owner_request_id != owner_request_id]
                if records:
                    self._embargoes_by_scope[scope_key] = records
                elif scope_key in self._embargoes_by_scope:
                    del self._embargoes_by_scope[scope_key]

    def find_embargoes(self, scope_keys: Iterable[str]) -> Tuple[str, ...]:
        """
        Return scope keys that are currently embargoed.

        Purpose:
            Provide embargo evidence for admission checks.
        Contract:
            - Returns an empty tuple when no embargoes apply.
        Args:
            scope_keys:
                Scope keys to check for embargo status.
        Returns:
            Tuple[str, ...]:
                Embargoed scope keys.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while checking registries.
        """
        self.check_cleaned()
        blocked: List[str] = []
        with self._lock:
            for scope_key in scope_keys:
                if scope_key in self._embargoes_by_scope:
                    blocked.append(scope_key)
        return tuple(blocked)

    def apply_implicit_embargoes(self, request: ChangeControlTransactionRequest) -> None:
        """
        Scaffolding hook for implicit embargo rules (bind/link/etc.).

        Purpose:
            Reserve a place for orchestrator-driven implicit embargo policies.
        Contract:
            - No-op until policies are defined.
        Args:
            request:
                Admitted request for which to apply implicit embargoes.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Safe for concurrent use; no internal state is mutated.
        """
        self.check_cleaned()
        _ = request

    def release_implicit_embargoes(self, request: ChangeControlTransactionRequest) -> None:
        """
        Scaffolding hook for releasing implicit embargoes.

        Purpose:
            Reserve a place for orchestrator-driven embargo release policies.
        Contract:
            - No-op until policies are defined.
        Args:
            request:
                Admitted request whose implicit embargoes should be released.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Safe for concurrent use; no internal state is mutated.
        """
        self.check_cleaned()
        _ = request

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot for embargo manager state.

        Purpose:
            Provide a concise view of active embargo scopes.
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
        self.check_cleaned()
        with self._lock:
            return {
                "embargoed_scopes": list(self._embargoes_by_scope.keys()),
                "embargo_count": sum(len(v) for v in self._embargoes_by_scope.values()),
            }
