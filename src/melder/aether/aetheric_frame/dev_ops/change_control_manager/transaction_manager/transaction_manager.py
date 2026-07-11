import time
import uuid
import hashlib
from threading import RLock
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TYPE_CHECKING,
    ClassVar,
)

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
)
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeTransactionType,
    )



class ChangeControlTransactionManager(Cleanable):
    """
    Transaction-bookkeeping root for change-control admission.

    This manager owns the state that surrounds admission rather than the
    admission decision itself. The higher-level orchestrator decides whether a
    request is accepted; this manager is where that accepted request is turned
    into durable operational bookkeeping.

    Owned state:
    - the in-flight request registry
    - the provider-to-borrower link mirror
    - the optional audit callback for admitted requests

    Contract:
    - In-flight registry reflects admitted requests only.
    - Link-mirror data is support/diagnostic state unless future policy
      explicitly promotes it into admission logic.
    - Audit logging, when configured, runs outside the manager lock.
    - Cleanup is idempotent and invalidates the manager for future use.

    Practical role in the system:
    - build immutable request payloads before admission
    - track which requests are currently in-flight after admission
    - provide normalized scope-key builders used by conflict and embargo logic
    - mirror active conduit links for diagnostics and possible future policy
      expansion

    Threading:
    - Shared state mutation is guarded by an internal `RLock`.
    - Pure formatting/hash helpers do not require the lock because they do not
      mutate manager state.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
        - Starts with empty in-flight and link-mirror registries.
        - `_audit_log_fn` starts disabled (`None`).
        - Safe to publish immediately after construction.

        The manager intentionally starts with no ambient state beyond those
        registries; all request and link information is learned through explicit
        admission / link-tracking calls.
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
        - After cleanup, public methods fail through `check_cleaned()`.

        Cleanup does not attempt any external side effects. Its job is only to
        tear down this manager's owned bookkeeping so stale transaction state
        cannot survive past the lifetime of the owning DevOps surface.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._in_flight is not None:
                self._in_flight.clear()
            if self._link_mirror is not None:
                for borrowers in self._link_mirror.values():
                    borrowers.clear()
                self._link_mirror.clear()

            del self._in_flight
            del self._link_mirror
            del self._audit_log_fn
        del self._lock

    def set_audit_logger(
            self,
            fn: Optional[Callable[[ChangeControlTransactionRequest], None]],
    ) -> None:
        """
        Register a callback to log admitted transaction requests.

        Contract:
        - Passing `None` disables audit logging.
        - The callback reference is stored under the lock, but invocation
          happens later outside the lock.
        - The callback is observational only; it does not participate in
          admission correctness.

        Args:
            fn: Callable that receives admitted requests, or `None`.
        """
        
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
            scope_claims: Optional[Iterable[Tuple[str, str]]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> ChangeControlTransactionRequest:
        """
        Build a new immutable transaction request payload.

        Contract:
        - Generates a fresh `request_id` and `created_at` timestamp.
        - Normalizes iterable fields into tuples.
        - Validates `scope_claims` modes through `ClaimMode` and stores them
          as `(scope_key, mode_value)` pairs; keys without explicit claims
          default to exclusive mode at admission.
        - Derives scope hashes from `scope_keys` when hashes are omitted.
        - Does not register the request as in-flight or mutate manager state.

        This method is the canonical request-construction surface for
        change-control callers. It creates the immutable payload that later
        flows through conflict checks, embargo checks, staged mutation records,
        and in-flight tracking.

        Args:
            request_type: Transaction kind to record.
            initiator_conduit_id: Conduit id that initiated the transaction.
            spellbook_id: Optional spellbook id associated with the request.
            conduit_ids: Optional conduit ids touched by the request.
            scope_keys: Optional normalized scope keys.
            scope_claims: Optional `(scope_key, mode)` pairs declaring
                per-scope claim modes for acquisition.
            scope_hashes: Optional normalized scope hashes.
            binding_keys: Optional binding keys affected by the request.
            contract_keys: Optional contract keys affected by the request.
            metadata: Optional structured metadata for diagnostics.

        Returns:
            ChangeControlTransactionRequest: Immutable request payload ready for
            admission evaluation.
        Raises:
            RuntimeError: If the manager has been cleaned.
            TypeError: If initiator_conduit_id is not a string.
            ValueError: If initiator_conduit_id is empty.
        Threading:
            Thread-safe without lock; no shared state is mutated.
        """
        
        if not isinstance(initiator_conduit_id, str):
            raise TypeError("initiator_conduit_id must be a string.")
        if not initiator_conduit_id.strip():
            raise ValueError("initiator_conduit_id must not be empty.")
        request_id = f"tx-{uuid.uuid4().hex}"
        created_at = time.time()
        normalized_scope_keys = tuple(scope_keys) if scope_keys else ()
        normalized_scope_claims: Tuple[Tuple[str, str], ...] = ()
        if scope_claims:
            from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
                ClaimMode,
            )
            normalized_scope_claims = tuple(
                (scope_key, ClaimMode(raw_mode).value)
                for scope_key, raw_mode in scope_claims
                if scope_key
            )
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
            scope_claims=normalized_scope_claims,
            scope_hashes=normalized_scope_hashes,
            binding_keys=tuple(binding_keys) if binding_keys else (),
            contract_keys=tuple(contract_keys) if contract_keys else (),
            metadata=dict(metadata) if metadata else {},
        )

    def _normalize_scope_hashes(self, scope_keys: Iterable[str]) -> Tuple[str, ...]:
        """
        Derive deterministic SHA256 scope hashes from raw scope keys.

        Contract:
        - Keys are de-duplicated and sorted first so the output is stable
          for the same logical set regardless of input order.
        - Each normalized key is hashed with SHA256.

        This keeps downstream conflict logic deterministic even when callers
        provide keys in different orders or repeat the same scope key more than
        once.

        Args:
            scope_keys: Raw scope keys to normalize and hash.

        Returns:
            Tuple[str, ...]: Deterministic scope hash values.
        """
        
        unique_keys = sorted({key for key in scope_keys if key})
        hashes: List[str] = []
        for key in unique_keys:
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
            hashes.append(digest)
        return tuple(hashes)

    def make_scope_key_spellbook(self, spellbook_id: str) -> str:
        """
        Build a normalized spellbook scope key.

        This is the broadest transaction scope helper in the file. It is used
        when a request should be considered to touch an entire spellbook rather
        than one narrower binding, contract, or conduit slice.

        Returns:
            str: Scope key in the form `"scope:spellbook:<id>"`.
        """
        
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty")
        return f"scope:spellbook:{spellbook_id}"

    def make_scope_key_identity(
            self,
            *,
            owner_kind: str,
            owner_id: str,
    ) -> str:
        """
        Build a normalized broad object scope key for one identity.

        Purpose:
            Provide a generic scope helper for runtime assets that should be
            locked as objects, but do not have their own narrower helper like
            spellbook, conduit, or cluster.

        Args:
            owner_kind:
                Identity kind label such as `conduit_ward`.
            owner_id:
                Stable owner identifier for that object.

        Returns:
            str:
                Scope key in the form `"scope:<owner_kind>:<owner_id>"`.
        """
        
        if not owner_kind:
            raise ValueError("owner_kind cannot be empty")
        if not owner_id:
            raise ValueError("owner_id cannot be empty")
        return f"scope:{owner_kind}:{owner_id}"

    def make_scope_key_transaction_owner(
            self,
            *,
            owner_kind: str,
            owner_id: str,
            transaction_name: str,
    ) -> str:
        """
        Build one normalized transaction-owner scope key.

        Purpose:
            Provide a strategy-side scope helper for transaction families that
            need to embargo or conflict on a specific owner + transaction kind
            pair rather than only on the broad spellbook/conduit scope.

        Args:
            owner_kind:
                Owner kind label such as `spellbook` or `conduit`.
            owner_id:
                Stable owner identifier.
            transaction_name:
                Lower-level transaction name tied to the embargoed action.

        Returns:
            str:
                Scope key in the form
                `"scope:transaction:<owner_kind>:<owner_id>:<transaction_name>"`.
        """
        
        if not owner_kind:
            raise ValueError("owner_kind cannot be empty")
        if not owner_id:
            raise ValueError("owner_id cannot be empty")
        if not transaction_name:
            raise ValueError("transaction_name cannot be empty")
        return (
            f"scope:transaction:{owner_kind}:{owner_id}:{transaction_name}"
        )

    def make_scope_key_conduit(self, conduit_id: str) -> str:
        """
        Build a normalized conduit scope key.

        This helper is used when admission should reason about one conduit as a
        conflict/embargo unit.

        Returns:
            str: Scope key in the form `"scope:conduit:<id>"`.
        """
        
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty")
        return f"scope:conduit:{conduit_id}"

    def make_scope_key_cluster(self, cluster_id: str) -> str:
        """
        Build a normalized cluster scope key.

        This is the cluster-level counterpart to the spellbook/conduit scope
        helpers and is intended for requests that conceptually touch one shared
        conduit-cluster surface.

        Returns:
            str: Scope key in the form `"scope:cluster:<id>"`.
        """
        
        if not cluster_id:
            raise ValueError("cluster_id cannot be empty")
        return f"scope:cluster:{cluster_id}"

    def make_scope_key_binding(self, frame_key: str, binding_key: str) -> str:
        """
        Build a normalized binding scope key.

        This is the narrow "one frame/binding slot" scope helper used when
        conflict or embargo checks should reason about one logical binding
        location rather than the larger spellbook or conduit that contains it.

        Returns:
            str: Scope key in the form `"binding:<frame_key>:<binding_key>"`.
        """
        
        if not frame_key or not binding_key:
            raise ValueError("frame_key and binding_key are required")
        return f"binding:{frame_key}:{binding_key}"

    def make_scope_key_lineage(self, spell_index_id: str) -> str:
        """
        Build a normalized lineage scope key.

        Purpose:
            The remediation-mediation vocabulary (owner ruling
            2026-07-12: mediate both threads): one scope naming a single
            SpellIndex lineage, claimed EXCLUSIVE by the remediation
            transaction family and added to the membership families'
            seals (notch/add/remove/transfer) so a lazy revalidation
            window and a membership repoint on the SAME lineage
            provably serialize.

        Args:
            spell_index_id:
                The lineage's stable SpellIndex ULID.

        Returns:
            str: Scope key in the form `"lineage:<spell_index_id>"`.

        Raises:
            ValueError: If `spell_index_id` is empty.
        """
        if not spell_index_id:
            raise ValueError("spell_index_id is required")
        return f"lineage:{spell_index_id}"

    def make_scope_key_contract(
            self,
            frame_key: str,
            binding_key: str,
            peer_conduit_id: str,
    ) -> str:
        """
        Build a normalized contract scope key.

        This is the contract-facing scope helper used when a request should be
        scoped to one borrower/provider contract edge rather than to an entire
        binding surface.

        Returns:
            str: Scope key in the form
            `"contract:<frame_key>:<binding_key>:<peer_conduit_id>"`.
        """
        
        if not frame_key or not binding_key or not peer_conduit_id:
            raise ValueError("frame_key, binding_key, and peer_conduit_id are required")
        return f"contract:{frame_key}:{binding_key}:{peer_conduit_id}"

    def add_in_flight(self, request: ChangeControlTransactionRequest) -> None:
        """
        Track a request as in-flight and emit audit log if configured.

        Contract:
        - Replaces any older entry with the same request id.
        - Invokes the audit callback, when configured, after the registry
          update and outside the lock.

        This is the handoff point between admission and lifecycle tracking:
        once a request is added here, the rest of the change-control system may
        treat it as active until commit or abort removes it again.
        """
        
        audit_fn: Optional[Callable[[ChangeControlTransactionRequest], None]] = None
        with self._lock:
            self._in_flight[request.request_id] = request
            audit_fn = self._audit_log_fn
        if audit_fn is not None:
            audit_fn(request)

    def remove_in_flight(self, request_id: str) -> None:
        """
        Remove a request from the in-flight registry.

        Contract:
        - Missing request ids are ignored so commit/abort cleanup can call this
          method without pre-checking for presence.
        - Removal only affects the in-flight registry; it does not touch the
          link mirror or any external embargo state.
        """
        
        with self._lock:
            if request_id in self._in_flight:
                del self._in_flight[request_id]

    def list_in_flight(self) -> List[ChangeControlTransactionRequest]:
        """
        Return a snapshot list of in-flight requests.

        The returned list is a snapshot, not a live view, so callers can inspect
        it without mutating manager state or holding the lock.

        Returns:
            List[ChangeControlTransactionRequest]: New list snapshot of the
            current in-flight registry.
        """
        
        with self._lock:
            return list(self._in_flight.values())

    def get_in_flight(self, request_id: str) -> Optional[ChangeControlTransactionRequest]:
        """
        Return an in-flight request by id, if present.

        This is the direct lookup path used by commit/abort and other lifecycle
        flows that need the original immutable request payload after admission.

        Returns:
            Optional[ChangeControlTransactionRequest]: The tracked request, or
            `None` when the id is not currently in flight.
        """
        
        with self._lock:
            return self._in_flight.get(request_id)

    def register_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Track an active link (borrower -> provider) for diagnostics or future
        admission policy checks.

        Contract:
        - The mirror is keyed by provider conduit id.
        - Borrowers are stored in a set, so repeated registration of the same
          borrower/provider pair is naturally deduplicated.

        This mirror is descriptive state today, but it is shaped so future
        admission policy could reason about borrower/provider fan-out without
        redesigning the registry.
        """
        
        if not borrower_conduit_id or not provider_conduit_id:
            raise ValueError("borrower_conduit_id and provider_conduit_id are required")
        with self._lock:
            self._link_mirror.setdefault(provider_conduit_id, set()).add(borrower_conduit_id)

    def unregister_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
        """
        Remove a tracked link (borrower -> provider).

        Contract:
        - Missing links are ignored so teardown paths can call this without
          pre-checking membership.
        - If a provider no longer has any tracked borrowers after removal, its
          mirror entry is removed entirely.
        """
        
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

        This exposes the provider-to-borrower mirror as a detached set snapshot
        so diagnostics can inspect current fan-out without mutating manager
        state.

        Contract:
        - Returns an empty set for blank or unknown provider ids.
        - The returned set is detached from manager state.

        Returns:
            Set[str]: New set snapshot of borrower conduit ids currently
            mirrored under the provider.
        """
        
        if not provider_conduit_id:
            return set()
        with self._lock:
            return set(self._link_mirror.get(provider_conduit_id, set()))

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot for transaction manager state.

        This is the compact introspection surface for the manager itself:
        enough to understand how many requests are in flight and what the
        provider-to-borrower mirror currently contains, without exposing live
        internal containers.

        Returns:
            Dict[str, Any]: Snapshot metadata for current in-flight request
            count and the provider-to-borrower mirror.
        """
        
        with self._lock:
            return {
                "in_flight_count": len(self._in_flight),
                "link_mirror": {k: set(v) for k, v in self._link_mirror.items()},
            }
