import time
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Iterable, List, Set, Tuple, TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )


@dataclass(frozen=True)
class ChangeControlEmbargoRecord:
    """
    Immutable record describing one embargoed scope key.

    Purpose:
        Capture one request-owned embargo entry in a form that admission,
        diagnostics, and advisory tooling can share safely.

    Contract:
        - Each record ties one normalized scope key to the request that opened
          the embargo.
        - `reason_tag` carries the lightweight operational reason associated
          with the embargo, such as the admitted transaction type.
        - Records are immutable and may be copied freely across threads or
          tooling boundaries.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    scope_key: str
    reason_tag: str
    owner_request_id: str
    created_at: float


class ChangeControlEmbargoManager(Cleanable):
    """
    Scope-key embargo registry for transaction-driven gating.

    This manager tracks temporary embargoes opened by admitted change-control
    requests. Those embargoes are used during later admission checks so new
    requests can be rejected or hinted away from scope that is already owned by
    an in-flight request.

    Contract:
    - Embargoes are owned by request id, not by standalone lifecycle objects.
    - Scope and owner indexes stay in sync.
    - Commit/abort flows release embargoes through the owner-request path.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_embargoes_by_scope",
        "_embargoes_by_owner",
    ]

    def __init__(self) -> None:
        """
        Initialize the embargo registry.

        Contract:
        - Starts with empty scope and owner indexes.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._embargoes_by_scope: Dict[str, List[ChangeControlEmbargoRecord]] = {}
        self._embargoes_by_owner: Dict[str, Set[str]] = {}

    def cleanup(self) -> None:
        """
        Finalize the embargo registry.

        Contract:
        - Idempotent cleanup.
        - Clears both embargo indexes before dropping the lock reference.
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
        del self._lock

    def open_embargo(
            self,
            *,
            scope_keys: Iterable[str],
            reason_tag: str,
            owner_request_id: str,
    ) -> None:
        """
        Open embargoes for the supplied scope keys.

        Each supplied scope key becomes associated with the owning request id.
        Multiple embargo records may accumulate for the same scope when
        different in-flight requests independently embargo it.

        Args:
            scope_keys: Scope keys to embargo.
            reason_tag: Short diagnostic reason for the embargo.
            owner_request_id: Request id that owns the embargoes.
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

    def extend_embargoes(
            self,
            *,
            owner_request_id: str,
            scope_keys: Iterable[str],
            reason_tag: str,
    ) -> None:
        """
        Extend embargoes for an existing request with additional scope keys.

        This is the staged-update path for requests that discover new scope
        after admission. Existing embargoes for the same owner are preserved;
        only genuinely new scope keys are added.

        Args:
            owner_request_id: Request id that owns the embargoes.
            scope_keys: Additional scope keys to embargo.
            reason_tag: Diagnostic reason tag for the new records.
        """
        self.check_cleaned()
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
                )
                self._embargoes_by_scope.setdefault(scope_key, []).append(record)
                self._embargoes_by_owner.setdefault(owner_request_id, set()).add(scope_key)
                existing.add(scope_key)

    def close_embargo(self, owner_request_id: str) -> None:
        """
        Close all embargoes owned by the supplied request id.

        This is the normal release path after commit or abort. If the request
        has no active embargoes, the method simply no-ops.

        Args:
            owner_request_id: Request id whose embargoes should be released.
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

        This is the query surface used by admission logic when it needs to know
        whether any requested scope is currently embargoed.

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

    def list_advisory_hints(
            self,
            scope_keys: Iterable[str],
    ) -> Tuple[ChangeControlEmbargoRecord, ...]:
        """
        Return advisory embargo records for the supplied scope keys.

        Purpose:
            Provide soft-lock hints that agents can honor before mutation.
        Contract:
            - Returns a tuple of embargo records (may be empty).
            - Does not block or mutate state.
        Args:
            scope_keys:
                Scope keys to check for advisory hints.
        Returns:
            Tuple[ChangeControlEmbargoRecord, ...]:
                Embargo records covering the supplied scopes.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while copying records.
        """
        self.check_cleaned()
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
            request: ChangeControlTransactionRequest,
    ) -> Tuple[str, ...]:
        """
        Build a scope-key set for embargo checks from a request payload.

        Purpose:
            Normalize scope keys used for implicit embargo checks to ensure
            admission uses consistent scope comparisons.
        Contract:
            - Includes request.scope_keys.
            - Adds derived spellbook/conduit/binding/contract scopes when present.
        Args:
            request:
                Transaction request to normalize.
        Returns:
            Tuple[str, ...]:
                Normalized scope keys for embargo checks.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        return self._collect_scope_keys_from_fields(
            scope_keys=request.scope_keys,
            spellbook_id=request.spellbook_id,
            conduit_ids=request.conduit_ids,
            binding_keys=request.binding_keys,
            contract_keys=request.contract_keys,
        )

    def collect_scope_keys_from_staged(
            self,
            staged: ChangeControlStagedMutation,
    ) -> Tuple[str, ...]:
        """
        Build scope keys for embargo checks from staged mutation metadata.

        Purpose:
            Normalize scope keys when staged metadata updates occur after admission.
        Contract:
            - Returns an empty tuple if staged is None.
        Args:
            staged:
                Staged mutation to normalize.
        Returns:
            Tuple[str, ...]:
                Normalized scope keys for embargo checks.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
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
            spellbook_id: str | None,
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
                Normalized scope keys for embargo checks.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
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


    def apply_implicit_embargoes(self, request: ChangeControlTransactionRequest) -> None:
        """
        Scaffolding hook for implicit embargo rules (bind/link/etc.).

        Purpose:
            Apply implicit embargoes for the admitted request.
        Contract:
            - Opens embargoes for derived scope keys tied to the request.
        Args:
            request:
                Admitted request for which to apply implicit embargoes.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while updating registries.
        """
        self.check_cleaned()
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

    def release_implicit_embargoes(self, request: ChangeControlTransactionRequest) -> None:
        """
        Scaffolding hook for releasing implicit embargoes.

        Purpose:
            Release implicit embargoes opened for the supplied request.
        Contract:
            - Closes all embargoes owned by the request id.
            - Mutates the embargo registry through `close_embargo(...)`; this
              is not a read-only diagnostic helper.
        Args:
            request:
                Admitted request whose implicit embargoes should be released.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Delegates to `close_embargo(...)`, which mutates registry state
            under the manager lock.
        """
        self.check_cleaned()
        self.close_embargo(request.request_id)

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
