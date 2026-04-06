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
    Transaction bookkeeping and scope-key utility surface for change control.

    This manager owns three related pieces of state:
    - in-flight request registry
    - provider-to-borrower link mirror
    - optional audit callback for admitted requests

    Contract:
    - In-flight registry reflects admitted requests only.
    - Link mirror is diagnostic/support state unless future policy promotes it
      into admission logic.
    - Audit logging, when configured, runs outside the manager lock.
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

        Contract:
        - `_in_flight` and `_link_mirror` start empty.
        - `_audit_log_fn` starts disabled (`None`).
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._in_flight: Dict[str, ChangeControlTransactionRequest] = {}
        # provider_conduit_id -> set[borrower_conduit_id]
        self._link_mirror: Dict[str, Set[str]] = {}
        self._audit_log_fn: Optional[Callable[[ChangeControlTransactionRequest], None]] = None

    def cleanup(self) -> None:
        """
        Finalize the transaction manager.

        Contract:
        - Idempotent cleanup.
        - Clears the in-flight registry, link mirror, and audit callback before
          dropping the lock reference.
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

        Passing `None` disables audit logging. The callback is stored under the
        manager lock but invoked later outside the lock.
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

        This is a pure payload-construction helper. It normalizes tuples,
        generates ids/timestamps, and optionally derives scope hashes, but it
        does not register the request as in-flight.

        Args:
            request_type: Transaction kind to record.
            initiator_conduit_id: Conduit id that initiated the transaction.
            spellbook_id: Optional spellbook id associated with the request.
            conduit_ids: Optional conduit ids touched by the request.
            scope_keys: Optional normalized scope keys.
            scope_hashes: Optional normalized scope hashes.
            binding_keys: Optional binding keys affected by the request.
            contract_keys: Optional contract keys affected by the request.
            metadata: Optional structured metadata for diagnostics.
        Returns:
            ChangeControlTransactionRequest: Immutable request payload.
        Raises:
            RuntimeError: If the manager has been cleaned.
            TypeError: If initiator_conduit_id is not a string.
            ValueError: If initiator_conduit_id is empty.
        Threading:
            Thread-safe without lock; no shared state is mutated.
        """
        self.check_cleaned()
        if not isinstance(initiator_conduit_id, str):
            raise TypeError("initiator_conduit_id must be a string.")
        if not initiator_conduit_id.strip():
            raise ValueError("initiator_conduit_id must not be empty.")
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
        Derive deterministic SHA256 scope hashes from raw scope keys.

        Keys are de-duplicated and sorted first so callers get stable hash
        tuples regardless of input order.
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

        Returns:
            str: Scope key in the form `"scope:spellbook:<id>"`.
        """
        self.check_cleaned()
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty")
        return f"scope:spellbook:{spellbook_id}"

    def make_scope_key_conduit(self, conduit_id: str) -> str:
        """
        Build a normalized conduit scope key.

        Returns:
            str: Scope key in the form `"scope:conduit:<id>"`.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty")
        return f"scope:conduit:{conduit_id}"

    def make_scope_key_cluster(self, cluster_id: str) -> str:
        """
        Build a normalized cluster scope key.

        Returns:
            str: Scope key in the form `"scope:cluster:<id>"`.
        """
        self.check_cleaned()
        if not cluster_id:
            raise ValueError("cluster_id cannot be empty")
        return f"scope:cluster:{cluster_id}"

    def make_scope_key_binding(self, frame_key: str, binding_key: str) -> str:
        """
        Build a normalized binding scope key.

        Returns:
            str: Scope key in the form `"binding:<frame_key>:<binding_key>"`.
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

        Returns:
            str: Scope key in the form
            `"contract:<frame_key>:<binding_key>:<peer_conduit_id>"`.
        """
        self.check_cleaned()
        if not frame_key or not binding_key or not peer_conduit_id:
            raise ValueError("frame_key, binding_key, and peer_conduit_id are required")
        return f"contract:{frame_key}:{binding_key}:{peer_conduit_id}"

    def add_in_flight(self, request: ChangeControlTransactionRequest) -> None:
        """
        Track a request as in-flight and emit audit log if configured.

        The request replaces any older entry with the same id. If an audit
        callback is configured, it is invoked after the registry update and
        outside the lock.
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

        Missing request ids are ignored so commit/abort cleanup can safely call
        this method without pre-checking for presence.
        """
        self.check_cleaned()
        with self._lock:
            if request_id in self._in_flight:
                del self._in_flight[request_id]

    def list_in_flight(self) -> List[ChangeControlTransactionRequest]:
        """
        Return a snapshot list of in-flight requests.

        Returns:
            List[ChangeControlTransactionRequest]: New list snapshot of the
            current in-flight registry.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._in_flight.values())

    def get_in_flight(self, request_id: str) -> Optional[ChangeControlTransactionRequest]:
        """
        Return an in-flight request by id, if present.

        Returns:
            Optional[ChangeControlTransactionRequest]: The tracked request, or
            `None` when the id is not currently in flight.
        """
        self.check_cleaned()
        with self._lock:
            return self._in_flight.get(request_id)

    def register_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Track an active link (borrower -> provider) for diagnostics or future
        admission policy checks.

        The link mirror is keyed by provider conduit id and stores borrower ids
        in a set, so repeated registration of the same borrower/provider pair is
        naturally deduplicated.
        """
        self.check_cleaned()
        if not borrower_conduit_id or not provider_conduit_id:
            raise ValueError("borrower_conduit_id and provider_conduit_id are required")
        with self._lock:
            self._link_mirror.setdefault(provider_conduit_id, set()).add(borrower_conduit_id)

    def unregister_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Remove a tracked link (borrower -> provider).

        If a provider no longer has any tracked borrowers after removal, its
        mirror entry is removed entirely.
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

        Returns:
            Set[str]: New set snapshot of borrower conduit ids currently
            mirrored under the provider.
        """
        self.check_cleaned()
        if not provider_conduit_id:
            return set()
        with self._lock:
            return set(self._link_mirror.get(provider_conduit_id, set()))

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot for transaction manager state.

        Returns:
            Dict[str, Any]: Snapshot metadata for current in-flight request
            count and the provider-to-borrower mirror.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "in_flight_count": len(self._in_flight),
                "link_mirror": {k: set(v) for k, v in self._link_mirror.items()},
            }
