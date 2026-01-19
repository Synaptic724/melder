import time
import uuid
import hashlib
from threading import RLock
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)


class ChangeControlTransactionManager(Cleanable):
    """
    Transaction manager for change-control admission.

    Purpose:
        Track in-flight transaction requests and maintain a link-mirror registry
        used by conflict and embargo checks.
    Contract:
        - In-flight registry is a snapshot of admitted requests.
        - Link mirror is keyed by provider conduit id and lists borrower conduits.
        - Audit logging is optional and invoked outside locks to avoid deadlocks.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Ownership:
        Owns the in-flight registry, link mirror registry, and audit callback reference.
    Threading:
        All state mutations are guarded by an internal RLock.
    Lifecycle:
        cleanup() is idempotent and nulls internal references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_in_flight",
        "_link_mirror",
        "_audit_log_fn",
    ]

    def __init__(self) -> None:
        """
        Initialize the transaction manager.

        Purpose:
            Set up empty registries for in-flight requests and link mirrors.
        Contract:
            - `_in_flight` and `_link_mirror` start empty.
            - `_audit_log_fn` starts as None (no-op).
        Returns:
            None.
        Threading:
            Safe to publish after initialization; internal lock guards state.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._in_flight: Dict[str, ChangeControlTransactionRequest] = {}
        # provider_conduit_id -> set[borrower_conduit_id]
        self._link_mirror: Dict[str, Set[str]] = {}
        self._audit_log_fn: Optional[Callable[[ChangeControlTransactionRequest], None]] = None

    def cleanup(self) -> None:
        """
        Idempotent cleanup for internal registries.

        Purpose:
            Release registries and callback references for GC safety.
        Contract:
            - Safe to call multiple times.
            - After cleanup, all public methods raise via check_cleaned().
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
            if self._in_flight is not None:
                self._in_flight.clear()
                self._in_flight = None
            if self._link_mirror is not None:
                for borrowers in self._link_mirror.values():
                    borrowers.clear()
                self._link_mirror.clear()
                self._link_mirror = None
            self._audit_log_fn = None
        self._lock = None

    def set_audit_logger(
            self,
            fn: Optional[Callable[[ChangeControlTransactionRequest], None]],
    ) -> None:
        """
        Register a callback to log admitted transaction requests.

        Purpose:
            Capture minimal audit metadata when a request is admitted.
        Contract:
            - Passing None disables audit logging.
            - Audit callback is stored but invoked outside the lock.
        Args:
            fn:
                Callable that receives the admitted request, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the callback.
        """
        self.check_cleaned()
        with self._lock:
            self._audit_log_fn = fn

    def build_request(
            self,
            *,
            request_type: ChangeTransactionType,
            initiator_conduit_id: str,
            spellbook_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> ChangeControlTransactionRequest:
        """
        Build a new immutable transaction request payload.

        Purpose:
            Create a normalized request object for admission checks.
        Contract:
            - Generates a new request_id and timestamp.
            - Does not register the request as in-flight.
        Args:
            request_type:
                Transaction type to record (bind/link/unlink/etc).
            initiator_conduit_id:
                Conduit id that initiated the transaction.
            spellbook_id:
                Optional spellbook id associated with the mutation.
            conduit_ids:
                Optional conduit ids touched by the mutation.
            scope_keys:
                Optional normalized scope keys.
            scope_hashes:
                Optional normalized scope hashes.
            binding_keys:
                Optional binding keys affected by the mutation.
            contract_keys:
                Optional contract keys affected by the mutation.
            metadata:
                Optional structured metadata for debugging.
        Returns:
            ChangeControlTransactionRequest:
                Immutable request payload.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without lock; no shared state is mutated.
        """
        self.check_cleaned()
        request_id = f"tx-{uuid.uuid4().hex}"
        created_at = time.time()
        normalized_scope_keys = tuple(scope_keys) if scope_keys else ()
        normalized_scope_hashes = tuple(scope_hashes) if scope_hashes else ()
        if normalized_scope_keys and not normalized_scope_hashes:
            normalized_scope_hashes = self._normalize_scope_hashes(normalized_scope_keys)
        return ChangeControlTransactionRequest(
            request_id=request_id,
            request_type=request_type,
            created_at=created_at,
            initiator_conduit_id=initiator_conduit_id,
            spellbook_id=spellbook_id,
            conduit_ids=tuple(conduit_ids) if conduit_ids else (),
            scope_keys=normalized_scope_keys,
            scope_hashes=normalized_scope_hashes,
            binding_keys=tuple(binding_keys) if binding_keys else (),
            contract_keys=tuple(contract_keys) if contract_keys else (),
            metadata=dict(metadata) if metadata else {},
        )

    def _normalize_scope_hashes(self, scope_keys: Iterable[str]) -> Tuple[str, ...]:
        """
        Internal

        Normalize scope hashes from supplied scope keys.

        Purpose:
            Provide deterministic scope hashes for conflict checks when callers
            supply only scope keys.
        Contract:
            - Keys are normalized by sorting and de-duplicating.
            - Each normalized key is hashed with SHA256.
        Args:
            scope_keys:
                Scope keys to normalize and hash.
        Returns:
            Tuple[str, ...]:
                Deterministic scope hash values.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        unique_keys = sorted({key for key in scope_keys if key})
        hashes: List[str] = []
        for key in unique_keys:
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
            hashes.append(digest)
        return tuple(hashes)

    def make_scope_key_spellbook(self, spellbook_id: str) -> str:
        """
        Build a normalized spellbook scope key.

        Purpose:
            Provide a stable key for conflict and embargo checks.
        Contract:
            - Returns "scope:spellbook:<id>".
        Args:
            spellbook_id:
                Spellbook identifier to normalize.
        Returns:
            str:
                Normalized spellbook scope key.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If spellbook_id is empty.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty")
        return f"scope:spellbook:{spellbook_id}"

    def make_scope_key_conduit(self, conduit_id: str) -> str:
        """
        Build a normalized conduit scope key.

        Purpose:
            Provide a stable key for conflict and embargo checks.
        Contract:
            - Returns "scope:conduit:<id>".
        Args:
            conduit_id:
                Conduit identifier to normalize.
        Returns:
            str:
                Normalized conduit scope key.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If conduit_id is empty.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty")
        return f"scope:conduit:{conduit_id}"

    def make_scope_key_cluster(self, cluster_id: str) -> str:
        """
        Build a normalized cluster scope key.

        Purpose:
            Provide a stable key for conflict and embargo checks.
        Contract:
            - Returns "scope:cluster:<id>".
        Args:
            cluster_id:
                Cluster identifier to normalize.
        Returns:
            str:
                Normalized cluster scope key.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If cluster_id is empty.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if not cluster_id:
            raise ValueError("cluster_id cannot be empty")
        return f"scope:cluster:{cluster_id}"

    def make_scope_key_binding(self, frame_key: str, binding_key: str) -> str:
        """
        Build a normalized binding scope key.

        Purpose:
            Provide a stable key for frame/binding conflict checks.
        Contract:
            - Returns "binding:<frame_key>:<binding_key>".
        Args:
            frame_key:
                Normalized frame key.
            binding_key:
                Normalized binding key.
        Returns:
            str:
                Normalized binding scope key.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If frame_key or binding_key is empty.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if not frame_key or not binding_key:
            raise ValueError("frame_key and binding_key are required")
        return f"binding:{frame_key}:{binding_key}"

    def make_scope_key_contract(
            self,
            frame_key: str,
            binding_key: str,
            peer_conduit_id: str,
    ) -> str:
        """
        Build a normalized contract scope key.

        Purpose:
            Provide a stable key for borrower/provider contract checks.
        Contract:
            - Returns "contract:<frame_key>:<binding_key>:<peer_conduit_id>".
        Args:
            frame_key:
                Normalized frame key.
            binding_key:
                Normalized binding key.
            peer_conduit_id:
                Peer conduit identifier involved in the contract.
        Returns:
            str:
                Normalized contract scope key.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If any identifier is empty.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        self.check_cleaned()
        if not frame_key or not binding_key or not peer_conduit_id:
            raise ValueError("frame_key, binding_key, and peer_conduit_id are required")
        return f"contract:{frame_key}:{binding_key}:{peer_conduit_id}"

    def add_in_flight(self, request: ChangeControlTransactionRequest) -> None:
        """
        Track a request as in-flight and emit audit log if configured.

        Purpose:
            Register the request in the in-flight registry after admission.
        Contract:
            - Audit callback is invoked without holding the lock.
            - The request replaces any existing entry with the same id.
        Args:
            request:
                Request to track.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock to update in-flight state.
        """
        self.check_cleaned()
        audit_fn: Optional[Callable[[ChangeControlTransactionRequest], None]] = None
        with self._lock:
            self._in_flight[request.request_id] = request
            audit_fn = self._audit_log_fn
        if audit_fn is not None:
            audit_fn(request)

    def remove_in_flight(self, request_id: str) -> None:
        """
        Remove a request from the in-flight registry.

        Purpose:
            Clear the in-flight record once a request is committed or aborted.
        Contract:
            - No error if the request id is absent.
        Args:
            request_id:
                Identifier of the request to remove.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock to update registry state.
        """
        self.check_cleaned()
        with self._lock:
            if request_id in self._in_flight:
                del self._in_flight[request_id]

    def list_in_flight(self) -> List[ChangeControlTransactionRequest]:
        """
        Return a snapshot list of in-flight requests.

        Purpose:
            Provide a stable view of currently admitted requests.
        Contract:
            - Returns a new list snapshot.
        Returns:
            List[ChangeControlTransactionRequest]:
                Snapshot of in-flight requests.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while copying.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._in_flight.values())

    def get_in_flight(self, request_id: str) -> Optional[ChangeControlTransactionRequest]:
        """
        Return an in-flight request by id, if present.

        Purpose:
            Allow callers to fetch the request payload for a known id.
        Contract:
            - Returns None when the request is not in-flight.
        Args:
            request_id:
                Identifier to look up.
        Returns:
            Optional[ChangeControlTransactionRequest]:
                The request payload if present.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock for the lookup.
        """
        self.check_cleaned()
        with self._lock:
            return self._in_flight.get(request_id)

    def register_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Track an active link (borrower -> provider) for conflict/embargo checks.

        Purpose:
            Update the link mirror registry to reflect a new contract link.
        Contract:
            - The provider key maps to a set of borrower conduit ids.
        Args:
            borrower_conduit_id:
                Conduit that borrows from the provider.
            provider_conduit_id:
                Conduit providing contracted spells.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If borrower or provider ids are empty.
        Threading:
            Acquires the internal lock while updating the mirror.
        """
        self.check_cleaned()
        if not borrower_conduit_id or not provider_conduit_id:
            raise ValueError("borrower_conduit_id and provider_conduit_id are required")
        with self._lock:
            self._link_mirror.setdefault(provider_conduit_id, set()).add(borrower_conduit_id)

    def unregister_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Remove a tracked link (borrower -> provider).

        Purpose:
            Update the link mirror registry to reflect a link removal.
        Contract:
            - If the provider has no remaining borrowers, its entry is removed.
        Args:
            borrower_conduit_id:
                Borrower conduit id to remove.
            provider_conduit_id:
                Provider conduit id to update.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
            ValueError: If borrower or provider ids are empty.
        Threading:
            Acquires the internal lock while updating the mirror.
        """
        self.check_cleaned()
        if not borrower_conduit_id or not provider_conduit_id:
            raise ValueError("borrower_conduit_id and provider_conduit_id are required")
        with self._lock:
            borrowers = self._link_mirror.get(provider_conduit_id)
            if borrowers is None:
                return
            borrowers.discard(borrower_conduit_id)
            if not borrowers:
                del self._link_mirror[provider_conduit_id]

    def list_borrowers_for_provider(self, provider_conduit_id: str) -> Set[str]:
        """
        Return the current borrower set for a provider conduit.

        Purpose:
            Provide a safe snapshot of borrower ids for a given provider.
        Contract:
            - Returns a new set; callers cannot mutate internal state.
        Args:
            provider_conduit_id:
                Provider conduit id to query.
        Returns:
            Set[str]:
                Snapshot of borrower conduit ids.
        Raises:
            RuntimeError: If the manager has been cleaned.
        Threading:
            Acquires the internal lock while copying.
        """
        self.check_cleaned()
        if not provider_conduit_id:
            return set()
        with self._lock:
            return set(self._link_mirror.get(provider_conduit_id, set()))

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot for transaction manager state.

        Purpose:
            Provide a concise view of current in-flight and link mirror state.
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
                "in_flight_count": len(self._in_flight),
                "link_mirror": {k: set(v) for k, v in self._link_mirror.items()},
            }
