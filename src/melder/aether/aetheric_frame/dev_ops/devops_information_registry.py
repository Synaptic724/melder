"""Aetheric frame dev-ops information registry.

This module owns one in-memory, frame-scoped index that mirrors high-value
operational topology for the running runtime:

- identity objects and optional identity object references,
- ownership relations between spellbooks and conduits,
- borrower/provider conduit link topology,
- conduit membership inside conduit clusters,
- live transaction objects with identity/type indexes.

The registry is intentionally **runtime-local and ephemeral**. It does not attempt
to be durable storage; it is a fast, consistent lookup surface for operational
components, reporting, and change-control support logic.

Design notes:

- All mutable states are kept in normal Python collections and guarded with an
  "RLock" for mutation/read consistency.
- Identity and relation updates are intended to be applied atomically per call.
- Missing keys passed to unregistered methods are treated as no-ops.
- "cleanup" tears down all indexes and internal references to prevent accidental
  post-cleanup reuse.
"""

import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_strategy_builder import (
    DevopsInformationStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


@dataclass(frozen=True)
class DevopsFactRecord:
    """
    Immutable last-reported fact baseline for one fact family in one region.

    Purpose:
        Record when one fact family for one region was last reported and by
        whom, so information strategies can skip re-derivation when every
        change since the baseline flowed through the transaction plane.

    Contract:
        - `fact_family` names the reported truth class (normally a
          transaction-type value such as `"bind"` or `"link"`).
        - `region` is a scope-shaped region key such as `"conduit:<id>"` or
          `"spellbook:<id>"`.
        - `last_reporter` is the request id or strategy execution that
          established the baseline; every fact traces to its reporter.
        - `generation` increments once per report for the same
          `(fact_family, region)` key.
        - Records are immutable and safe to share across threads.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    fact_family: str
    region: str
    last_reported_at: float
    last_reporter: str
    generation: int


class DevopsInformationRegistry(Cleanable):
    """
    Frame-local registry of dev-ops identities, relationships, and transaction
    metadata.

    Purpose
    -------
    Provide a single point of truth for indexing runtime topology relevant to
    dev-ops and control-plane workflows inside an "AethericFrame". The
    registry exposes efficient query paths while keeping the underlying data model
    explicit and inspectable.

    Data model
    ----------
    - Identity entries are keyed by "(owner_kind, owner_id)" and mapped to:
      - object identity (`_identities_by_key`)
      - optional object reference (`_objects_by_key`)
    - Ownership and graph relations are mirrored bidirectionally, so both traversal
      directions are O(1) for reads.
    - Transaction entries can be discovered by transaction id, participating identity,
      or transaction type.

    Contract
    --------
    - Belongs to exactly one frame name (`aetheric_frame_name`).
    - Public methods called "check_cleaned()" before accessing or mutating data.
    - Unregister operations are idempotent and do not raise when targets are absent.
    - "cleanup()" permanently retires the registry and deletes internal fields.
    - Every mutation and read method gets "self._lock" where index consistency
      is required.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_aetheric_frame_name",
        "_identities_by_key",
        "_objects_by_key",
        "_identity_keys_by_kind",
        "_spellbook_to_conduits",
        "_conduit_to_spellbook",
        "_provider_to_borrowers",
        "_borrower_to_providers",
        "_cluster_to_conduits",
        "_conduit_to_clusters",
        "_information_strategy_builder",
        "_transactions_by_id",
        "_transaction_ids_by_identity",
        "_transaction_ids_by_scope",
        "_transaction_ids_by_type",
        "_transaction_identity_keys_by_id",
        "_transaction_scope_keys_by_id",
        "_transaction_type_by_id",
        "_fact_records",
    ]

    def __init__(self, aetheric_frame_name: str) -> None:
        """
        Initialize a new frame-scoped registry.

        Parameters
        ----------
        aetheric_frame_name:
            The frame name this registry is scoped to. This value is treated as an
            immutable owner key for the life of the registry.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If "aetheric_frame_name" is not a string.
        ValueError
            If "aetheric_frame_name" is empty or whitespace.

        Notes
        -----
        Construction has no side effects outside the registry instance and does not
        touch global registries.
        """
        super().__init__()
        if not isinstance(aetheric_frame_name, str):
            raise TypeError("aetheric_frame_name must be a string.")
        if not aetheric_frame_name.strip():
            raise ValueError("aetheric_frame_name must not be empty.")

        self._lock: threading.RLock = threading.RLock()
        self._aetheric_frame_name: str = aetheric_frame_name
        self._identities_by_key: Dict[Tuple[str, str], "DevopsIdentity"] = {}
        self._objects_by_key: Dict[Tuple[str, str], Any] = {}
        self._identity_keys_by_kind: Dict[str, Set[Tuple[str, str]]] = {}
        self._spellbook_to_conduits: Dict[str, Set[str]] = {}
        self._conduit_to_spellbook: Dict[str, str] = {}
        self._provider_to_borrowers: Dict[str, Set[str]] = {}
        self._borrower_to_providers: Dict[str, Set[str]] = {}
        self._cluster_to_conduits: Dict[str, Set[str]] = {}
        self._conduit_to_clusters: Dict[str, Set[str]] = {}
        self._information_strategy_builder: DevopsInformationStrategyBuilder = (
            DevopsInformationStrategyBuilder(self)
        )
        self._transactions_by_id: Dict[str, Any] = {}
        self._transaction_ids_by_identity: Dict[Tuple[str, str], Set[str]] = {}
        self._transaction_ids_by_scope: Dict[str, Set[str]] = {}
        self._transaction_ids_by_type: Dict[str, Set[str]] = {}
        self._transaction_identity_keys_by_id: Dict[str, Set[Tuple[str, str]]] = {}
        self._transaction_scope_keys_by_id: Dict[str, Set[str]] = {}
        self._transaction_type_by_id: Dict[str, str] = {}
        self._fact_records: Dict[Tuple[str, str], "DevopsFactRecord"] = {}

    def cleanup(self) -> None:
        """
        Idempotently clear all registry states and retire the object.

        Returns
        -------
        None

        Behaviour
        --------
        1. No-op if already cleaned.
        2. Under lock:
           - marks the object as cleaned,
           - clears every mutable collection,
           - deletes internal storage fields.
        3. Releases lock and then deletes the lock reference to fully detach.

        Side Effects
        -----------
        - Drops all internal references to prevent accidental use after cleanup.
        - Subsequent public methods that call "check_cleaned()" will fail fast.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            for key_set in self._identity_keys_by_kind.values():
                key_set.clear()
            for conduit_ids in self._spellbook_to_conduits.values():
                conduit_ids.clear()
            for borrower_ids in self._provider_to_borrowers.values():
                borrower_ids.clear()
            for provider_ids in self._borrower_to_providers.values():
                provider_ids.clear()
            for conduit_ids in self._cluster_to_conduits.values():
                conduit_ids.clear()
            for cluster_ids in self._conduit_to_clusters.values():
                cluster_ids.clear()
            for transaction_ids in self._transaction_ids_by_identity.values():
                transaction_ids.clear()
            for transaction_ids in self._transaction_ids_by_scope.values():
                transaction_ids.clear()
            for transaction_ids in self._transaction_ids_by_type.values():
                transaction_ids.clear()

            self._identities_by_key.clear()
            self._objects_by_key.clear()
            self._identity_keys_by_kind.clear()
            self._spellbook_to_conduits.clear()
            self._conduit_to_spellbook.clear()
            self._provider_to_borrowers.clear()
            self._borrower_to_providers.clear()
            self._cluster_to_conduits.clear()
            self._conduit_to_clusters.clear()
            self._transactions_by_id.clear()
            self._transaction_ids_by_identity.clear()
            self._transaction_ids_by_scope.clear()
            self._transaction_ids_by_type.clear()
            self._transaction_identity_keys_by_id.clear()
            self._transaction_scope_keys_by_id.clear()
            self._transaction_type_by_id.clear()
            self._fact_records.clear()

            del self._identities_by_key
            del self._objects_by_key
            del self._identity_keys_by_kind
            del self._spellbook_to_conduits
            del self._conduit_to_spellbook
            del self._provider_to_borrowers
            del self._borrower_to_providers
            del self._cluster_to_conduits
            del self._conduit_to_clusters
            del self._information_strategy_builder
            del self._transactions_by_id
            del self._transaction_ids_by_identity
            del self._transaction_ids_by_scope
            del self._transaction_ids_by_type
            del self._transaction_identity_keys_by_id
            del self._transaction_scope_keys_by_id
            del self._transaction_type_by_id
            del self._fact_records
            del self._aetheric_frame_name
        del self._lock

    @property
    def aetheric_frame_name(self) -> str:
        """
        Return the owning frame name for this registry.

        Returns
        -------
        str
            The frame name captured at initialization.

        Raises
        ------
        RuntimeError
            If the registry has been cleaned.
        """
        
        return self._aetheric_frame_name

    @property
    def information_strategy_builder(self) -> DevopsInformationStrategyBuilder:
        """
        Return the registry-owned DevOps information-strategy builder.

        Returns
        -------
        DevopsInformationStrategyBuilder
            Builder that resolves registry-local information strategies.
        """

        return self._information_strategy_builder

    def report_fact(
            self,
            *,
            fact_family: str,
            region: str,
            reporter: str,
    ) -> DevopsFactRecord:
        """
        Record one last-reported fact baseline for a fact family and region.

        Parameters
        ----------
        fact_family:
            Truth class being reported (normally a transaction-type value).
        region:
            Scope-shaped region key such as "conduit:<id>" or
            "spellbook:<id>".
        reporter:
            Request id or strategy execution that establishes the baseline.

        Returns
        -------
        DevopsFactRecord
            The newly stored immutable record, with `generation` incremented
            from any prior record for the same key.

        Raises
        ------
        ValueError
            If any argument is empty.
        RuntimeError
            If the registry has been cleaned.

        Notes
        -----
        Transactions are the intended reporters: strategy commit deltas call
        this while the committing transaction still holds its scope claims,
        so baselines can never race overlapping writers.
        """
        self.check_cleaned()
        if not fact_family or not region or not reporter:
            raise ValueError("fact_family, region, and reporter are required.")
        with self._lock:
            key = (fact_family, region)
            previous = self._fact_records.get(key)
            record = DevopsFactRecord(
                fact_family=fact_family,
                region=region,
                last_reported_at=time.time(),
                last_reporter=reporter,
                generation=(previous.generation + 1) if previous is not None else 1,
            )
            self._fact_records[key] = record
            return record

    def get_fact_record(
            self,
            *,
            fact_family: str,
            region: str,
    ) -> Optional[DevopsFactRecord]:
        """
        Return the last-reported fact baseline for one family and region.

        Parameters
        ----------
        fact_family:
            Truth class to look up.
        region:
            Scope-shaped region key to look up.

        Returns
        -------
        Optional[DevopsFactRecord]
            The current baseline record, or None when the fact has never been
            reported (cold start; the asking strategy should derive and seed).

        Raises
        ------
        RuntimeError
            If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._fact_records.get((fact_family, region))

    def list_fact_records(
            self,
            *,
            region: Optional[str] = None,
    ) -> Tuple[DevopsFactRecord, ...]:
        """
        Return a snapshot of fact baselines, optionally filtered by region.

        Parameters
        ----------
        region:
            Optional region key; when supplied, only records for that region
            are returned.

        Returns
        -------
        Tuple[DevopsFactRecord, ...]
            Detached snapshot of matching records in stable key order.

        Raises
        ------
        RuntimeError
            If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if region is None:
                return tuple(
                    self._fact_records[key]
                    for key in sorted(self._fact_records.keys())
                )
            return tuple(
                self._fact_records[key]
                for key in sorted(self._fact_records.keys())
                if key[1] == region
            )

    def register_identity(
            self,
            identity: "DevopsIdentity",
            *,
            object_ref: Optional[Any] = None,
    ) -> None:
        """
        Register an identity and optional object reference for this frame.

        Parameters
        ----------
        identity:
            A "DevopsIdentity" to index under "(owner_kind, owner_id)".
        object_ref:
            Optional live object reference for the same identity key. If omitted, the
            identity can still be stored without an object payload.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If "identity" is "None" or belongs to a different frame.
        RuntimeError
            If another identity object is already registered for the same key.

        Notes
        -----
        The key is stored in "_identities_by_key" and optionally in
        "_objects_by_key". The owner-kind index "_identity_keys_by_kind" is also
        updated so callers can list all identities of a given kind.
        Spellbook<->conduit ownership is not derived here; it is maintained by
        explicit ownership-edge methods.
        """
        
        if identity is None:
            raise ValueError("identity must not be None.")
        if identity.aetheric_frame_name != self._aetheric_frame_name:
            raise ValueError(
                "Identity frame name does not match this registry's frame."
            )
        key = (identity.owner_kind, identity.owner_id)
        with self._lock:
            previous = self._identities_by_key.get(key)
            if previous is not None and previous is not identity:
                raise RuntimeError(
                    "A different identity is already registered for this key."
                )
            self._identities_by_key[key] = identity
            if object_ref is not None:
                self._objects_by_key[key] = object_ref
            elif key not in self._objects_by_key:
                self._objects_by_key[key] = None
            self._identity_keys_by_kind.setdefault(identity.owner_kind, set()).add(key)

    def unregister_identity(
            self,
            identity: Optional["DevopsIdentity"] = None,
            *,
            owner_kind: Optional[str] = None,
            owner_id: Optional[str] = None,
    ) -> None:
        """
        Unregister one identity and recursively clear associated relation edges.

        Parameters
        ----------
        identity:
            Identity object whose key should be removed.
        owner_kind:
            Identity kind when "identity" is not supplied.
        owner_id:
            Identity id when "identity" is not supplied.

        Returns
        -------
        None

        Behaviour
        --------
        - Resolves the key from either "identity" or "(owner_kind, owner_id)".
        - If the key is incomplete, no action is taken.
        - Deletes identity/object entries and the kind index entry.
        - Also removes any dependent graph edges:
          - conduit borrower/provider links,
          - conduit-cluster memberships,
          - transaction-by-identity references.

        Raises
        ------
        RuntimeError
            none; this method is intentionally idempotent for missing keys.
        """
        
        if identity is not None:
            owner_kind = identity.owner_kind
            owner_id = identity.owner_id
        if not owner_kind or not owner_id:
            return
        key = (owner_kind.strip().lower(), owner_id)
        with self._lock:
            self._identities_by_key.pop(key, None)
            self._objects_by_key.pop(key, None)
            kind_keys = self._identity_keys_by_kind.get(key[0])
            if kind_keys is not None:
                kind_keys.discard(key)
                if not kind_keys:
                    self._identity_keys_by_kind.pop(key[0], None)

            if key[0] == "spellbook":
                conduit_ids = set(self._spellbook_to_conduits.pop(key[1], set()))
                for conduit_id in conduit_ids:
                    mapped_spellbook_id = self._conduit_to_spellbook.get(conduit_id)
                    if mapped_spellbook_id == key[1]:
                        self._conduit_to_spellbook.pop(conduit_id, None)

            if key[0] == "conduit":
                spellbook_id = self._conduit_to_spellbook.pop(key[1], None)
                if spellbook_id is not None:
                    conduit_ids = self._spellbook_to_conduits.get(spellbook_id)
                    if conduit_ids is not None:
                        conduit_ids.discard(key[1])
                        if not conduit_ids:
                            self._spellbook_to_conduits.pop(spellbook_id, None)
                borrower_ids = set(self._provider_to_borrowers.pop(key[1], set()))
                for borrower_id in borrower_ids:
                    provider_ids = self._borrower_to_providers.get(borrower_id)
                    if provider_ids is not None:
                        provider_ids.discard(key[1])
                        if not provider_ids:
                            self._borrower_to_providers.pop(borrower_id, None)
                provider_ids = set(self._borrower_to_providers.pop(key[1], set()))
                for provider_id in provider_ids:
                    borrower_ids_for_provider = self._provider_to_borrowers.get(provider_id)
                    if borrower_ids_for_provider is not None:
                        borrower_ids_for_provider.discard(key[1])
                        if not borrower_ids_for_provider:
                            self._provider_to_borrowers.pop(provider_id, None)
                cluster_ids = set(self._conduit_to_clusters.pop(key[1], set()))
                for cluster_id in cluster_ids:
                    conduit_ids = self._cluster_to_conduits.get(cluster_id)
                    if conduit_ids is not None:
                        conduit_ids.discard(key[1])
                        if not conduit_ids:
                            self._cluster_to_conduits.pop(cluster_id, None)
            elif key[0] == "conduit_cluster":
                conduit_ids = set(self._cluster_to_conduits.pop(key[1], set()))
                for conduit_id in conduit_ids:
                    cluster_ids = self._conduit_to_clusters.get(conduit_id)
                    if cluster_ids is not None:
                        cluster_ids.discard(key[1])
                        if not cluster_ids:
                            self._conduit_to_clusters.pop(conduit_id, None)

            transaction_ids = set(self._transaction_ids_by_identity.pop(key, set()))
            for transaction_id in transaction_ids:
                identity_keys = self._transaction_identity_keys_by_id.get(transaction_id)
                if identity_keys is not None:
                    identity_keys.discard(key)

    def refresh_identity(
            self,
            identity: "DevopsIdentity",
            *,
            object_ref: Optional[Any] = None,
    ) -> None:
        """
        Refresh stored identity and optional object-reference snapshots.

        Purpose:
            Update the registered identity object and, optionally, its live
            object reference without rebuilding unrelated registry relations.

        Contract:
            - Identity must already belong to this frame.
            - Updates the optional object reference when supplied.
            - Does not derive or rebuild spellbook<->conduit ownership from
              identity metadata.

        Args:
            identity:
                Registered identity whose metadata changed.
            object_ref:
                Optional updated live object reference.

        Returns:
            None.
        """
        
        if identity is None:
            raise ValueError("identity must not be None.")
        if identity.aetheric_frame_name != self._aetheric_frame_name:
            raise ValueError(
                "Identity frame name does not match this registry's frame."
            )
        key = (identity.owner_kind, identity.owner_id)
        with self._lock:
            if key not in self._identities_by_key:
                raise RuntimeError("Identity is not registered in this registry.")
            self._identities_by_key[key] = identity
            if object_ref is not None:
                self._objects_by_key[key] = object_ref

    def register_spellbook_conduit_ownership(
            self,
            *,
            spellbook_id: str,
            conduit_id: str,
    ) -> None:
        """
        Register one explicit spellbook -> root-conduit ownership edge.

        Parameters
        ----------
        spellbook_id:
            Spellbook identifier that owns the root conduit.
        conduit_id:
            Root conduit identifier owned by the spellbook.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If either identifier is empty.
        """
        if not spellbook_id or not conduit_id:
            raise ValueError("spellbook_id and conduit_id are required.")
        with self._lock:
            previous_spellbook_id = self._conduit_to_spellbook.get(conduit_id)
            if previous_spellbook_id is not None and previous_spellbook_id != spellbook_id:
                conduit_ids = self._spellbook_to_conduits.get(previous_spellbook_id)
                if conduit_ids is not None:
                    conduit_ids.discard(conduit_id)
                    if not conduit_ids:
                        self._spellbook_to_conduits.pop(previous_spellbook_id, None)
            self._conduit_to_spellbook[conduit_id] = spellbook_id
            self._spellbook_to_conduits.setdefault(spellbook_id, set()).add(conduit_id)

    def unregister_spellbook_conduit_ownership(
            self,
            *,
            spellbook_id: str,
            conduit_id: str,
    ) -> None:
        """
        Remove one explicit spellbook -> root-conduit ownership edge.

        Parameters
        ----------
        spellbook_id:
            Spellbook identifier that owned the root conduit.
        conduit_id:
            Root conduit identifier to detach.

        Returns
        -------
        None
        """
        if not spellbook_id or not conduit_id:
            return
        with self._lock:
            mapped_spellbook_id = self._conduit_to_spellbook.get(conduit_id)
            if mapped_spellbook_id == spellbook_id:
                self._conduit_to_spellbook.pop(conduit_id, None)
            conduit_ids = self._spellbook_to_conduits.get(spellbook_id)
            if conduit_ids is not None:
                conduit_ids.discard(conduit_id)
                if not conduit_ids:
                    self._spellbook_to_conduits.pop(spellbook_id, None)

    def get_identity(
            self,
            *,
            owner_kind: str,
            owner_id: str,
    ) -> Optional["DevopsIdentity"]:
        """
        Resolve an identity by namespace/id.

        Parameters
        ----------
        owner_kind:
            Identity namespace (e.g., ""spellbook"", ""conduit"", ``"conduit_cluster"``).
        owner_id:
            Identity id value within the namespace.

        Returns
        -------
        DevopsIdentity | None
            The registered identity or "None" when no match exists.

        Notes
        -----
        "owner_kind" is normalized with "strip().lower()" before lookup.
        """
        
        if not owner_kind or not owner_id:
            return None
        with self._lock:
            return self._identities_by_key.get((owner_kind.strip().lower(), owner_id))

    def get_object(
            self,
            *,
            owner_kind: str,
            owner_id: str,
    ) -> Optional[Any]:
        """
        Resolve the object reference associated with an identity key.

        Parameters
        ----------
        owner_kind:
            Identity namespace.
        owner_id:
            Identity id value.

        Returns
        -------
        Any | None
            Stored object reference if present.

        Notes
        -----
        The key may exist without a concrete object reference. In that case "None"
        is returned from this lookup even when the identity itself exists.
        """
        
        if not owner_kind or not owner_id:
            return None
        with self._lock:
            return self._objects_by_key.get((owner_kind.strip().lower(), owner_id))

    def get_conduits_for_spellbook(self, spellbook_id: str) -> Tuple[str, ...]:
        """
        Return the conduits registered to a spellbook.

        Parameters
        ----------
        spellbook_id:
            Spellbook id to query.

        Returns
        -------
        tuple[str, ...]
            Sorted conduit ids for deterministic output.
        """
        
        if not spellbook_id:
            return tuple()
        with self._lock:
            return tuple(sorted(self._spellbook_to_conduits.get(spellbook_id, set())))

    def get_primary_conduit_id_for_spellbook(
            self,
            spellbook_id: str,
    ) -> Optional[str]:
        """
        Return the single paired conduit id for one spellbook, if present.

        Purpose
        -------
        Provide the direct spellbook -> root conduit lookup used by bind-family
        transaction planning, where the runtime contract expects at most one
        paired conduit after conjure.

        Parameters
        ----------
        spellbook_id:
            Spellbook id to resolve.

        Returns
        -------
        str | None
            The paired conduit id when present, otherwise `None`.

        Raises
        ------
        RuntimeError
            If more than one conduit id is currently registered for the
            spellbook, because that violates the current bind-family topology
            assumption.
        """
        
        conduit_ids = self.get_conduits_for_spellbook(spellbook_id)
        if not conduit_ids:
            return None
        if len(conduit_ids) > 1:
            raise RuntimeError(
                "Bind-family resolution expected one paired conduit for the spellbook, "
                f"but found {len(conduit_ids)}."
            )
        return conduit_ids[0]

    def get_conduit_objects_for_spellbook(self, spellbook_id: str) -> Tuple[Any, ...]:
        """
        Return live conduit objects currently mapped to one spellbook.

        Parameters
        ----------
        spellbook_id:
            Spellbook id to resolve through the derived ownership relation.

        Returns
        -------
        tuple[Any, ...]
            Live conduit objects currently known for the spellbook. Missing
            object references are skipped.
        """
        
        conduit_ids = self.get_conduits_for_spellbook(spellbook_id)
        objects: List[Any] = []
        for conduit_id in conduit_ids:
            conduit = self.get_object(owner_kind="conduit", owner_id=conduit_id)
            if conduit is not None:
                objects.append(conduit)
        return tuple(objects)

    def get_spellbook_for_conduit(self, conduit_id: str) -> Optional[str]:
        """
        Resolve the spellbook currently mapped to the conduit.

        Parameters
        ----------
        conduit_id:
            Conduit id to resolve.

        Returns
        -------
        str | None
            Owning spellbook id when present, else "None".
        """
        
        if not conduit_id:
            return None
        with self._lock:
            return self._conduit_to_spellbook.get(conduit_id)

    def get_spellbook_object_for_conduit(self, conduit_id: str) -> Optional[Any]:
        """
        Return the live spellbook object currently mapped to one conduit.

        Parameters
        ----------
        conduit_id:
            Conduit id whose owning spellbook should be resolved.

        Returns
        -------
        Any | None
            Live spellbook object when both the ownership relation and object
            reference are present, otherwise `None`.
        """
        
        spellbook_id = self.get_spellbook_for_conduit(conduit_id)
        if spellbook_id is None:
            return None
        return self.get_object(owner_kind="spellbook", owner_id=spellbook_id)

    def register_conduit_link(
            self,
            *,
            provider_conduit_id: str,
            borrower_conduit_id: str,
    ) -> None:
        """
        Register a provider -> borrower conduit dependency link.

        Parameters
        ----------
        provider_conduit_id:
            Provider conduit id.
        borrower_conduit_id:
            Borrower conduit id.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If either id is missing.

        Notes
        -----
        Maintains both:
        - "_provider_to_borrowers[provider]"
        - "_borrower_to_providers[borrower]"
        """
        
        if not provider_conduit_id or not borrower_conduit_id:
            raise ValueError(
                "provider_conduit_id and borrower_conduit_id are required."
            )
        with self._lock:
            self._provider_to_borrowers.setdefault(provider_conduit_id, set()).add(
                borrower_conduit_id
            )
            self._borrower_to_providers.setdefault(borrower_conduit_id, set()).add(
                provider_conduit_id
            )

    def unregister_conduit_link(
            self,
            *,
            provider_conduit_id: str,
            borrower_conduit_id: str,
    ) -> None:
        """
        Remove one provider -> borrower conduit relation edge.

        Parameters
        ----------
        provider_conduit_id:
            Provider conduit id.
        borrower_conduit_id:
            Borrower conduit id.

        Returns
        -------
        None

        Notes
        -----
        This is an idempotent operation and performs cleanup of empty edge buckets.
        """
        
        if not provider_conduit_id or not borrower_conduit_id:
            return
        with self._lock:
            borrower_ids = self._provider_to_borrowers.get(provider_conduit_id)
            if borrower_ids is not None:
                borrower_ids.discard(borrower_conduit_id)
                if not borrower_ids:
                    self._provider_to_borrowers.pop(provider_conduit_id, None)
            provider_ids = self._borrower_to_providers.get(borrower_conduit_id)
            if provider_ids is not None:
                provider_ids.discard(provider_conduit_id)
                if not provider_ids:
                    self._borrower_to_providers.pop(borrower_conduit_id, None)

    def list_borrowers_for_provider(self, provider_conduit_id: str) -> Tuple[str, ...]:
        """
        List all borrowers registered for a given provider conduit.

        Parameters
        ----------
        provider_conduit_id:
            Provider conduit id.

        Returns
        -------
        tuple[str, ...]
            Sorted borrower conduit ids. Empty tuple when unset.
        """
        
        if not provider_conduit_id:
            return tuple()
        with self._lock:
            return tuple(
                sorted(self._provider_to_borrowers.get(provider_conduit_id, set()))
            )

    def list_borrower_conduit_objects_for_provider(
            self,
            provider_conduit_id: str,
    ) -> Tuple[Any, ...]:
        """
        Return live borrower conduit objects for one provider conduit id.

        Parameters
        ----------
        provider_conduit_id:
            Provider conduit id used to resolve borrower edges.

        Returns
        -------
        tuple[Any, ...]
            Live borrower conduit objects. Missing object references are
            skipped.
        """
        
        borrower_ids = self.list_borrowers_for_provider(provider_conduit_id)
        borrowers: List[Any] = []
        for borrower_id in borrower_ids:
            borrower = self.get_object(owner_kind="conduit", owner_id=borrower_id)
            if borrower is not None:
                borrowers.append(borrower)
        return tuple(borrowers)

    def list_providers_for_borrower(self, borrower_conduit_id: str) -> Tuple[str, ...]:
        """
        List all providers registered for a given borrower conduit.

        Parameters
        ----------
        borrower_conduit_id:
            Borrower conduit id.

        Returns
        -------
        tuple[str, ...]
            Sorted provider conduit ids. Empty tuple when unset.
        """
        
        if not borrower_conduit_id:
            return tuple()
        with self._lock:
            return tuple(
                sorted(self._borrower_to_providers.get(borrower_conduit_id, set()))
            )

    def list_provider_conduit_objects_for_borrower(
            self,
            borrower_conduit_id: str,
    ) -> Tuple[Any, ...]:
        """
        Return live provider conduit objects for one borrower conduit id.

        Parameters
        ----------
        borrower_conduit_id:
            Borrower conduit id used to resolve provider edges.

        Returns
        -------
        tuple[Any, ...]
            Live provider conduit objects. Missing object references are
            skipped.
        """
        
        provider_ids = self.list_providers_for_borrower(borrower_conduit_id)
        providers: List[Any] = []
        for provider_id in provider_ids:
            provider = self.get_object(owner_kind="conduit", owner_id=provider_id)
            if provider is not None:
                providers.append(provider)
        return tuple(providers)

    def register_cluster_membership(
            self,
            *,
            cluster_id: str,
            conduit_id: str,
    ) -> None:
        """
        Register a conduit as a member of a cluster.

        Parameters
        ----------
        cluster_id:
            Cluster identifier.
        conduit_id:
            Conduit identifier.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If "cluster_id" or "conduit_id" are empty.

        Notes
        -----
        Updates both cluster->conduit and conduit->cluster indexes.
        """
        
        if not cluster_id or not conduit_id:
            raise ValueError("cluster_id and conduit_id are required.")
        with self._lock:
            self._cluster_to_conduits.setdefault(cluster_id, set()).add(conduit_id)
            self._conduit_to_clusters.setdefault(conduit_id, set()).add(cluster_id)

    def unregister_cluster_membership(
            self,
            *,
            cluster_id: str,
            conduit_id: str,
    ) -> None:
        """
        Remove a conduit from a specific cluster membership edge.

        Parameters
        ----------
        cluster_id:
            Cluster identifier.
        conduit_id:
            Conduit identifier.

        Returns
        -------
        None
        """
        
        if not cluster_id or not conduit_id:
            return
        with self._lock:
            conduit_ids = self._cluster_to_conduits.get(cluster_id)
            if conduit_ids is not None:
                conduit_ids.discard(conduit_id)
                if not conduit_ids:
                    self._cluster_to_conduits.pop(cluster_id, None)
            cluster_ids = self._conduit_to_clusters.get(conduit_id)
            if cluster_ids is not None:
                cluster_ids.discard(cluster_id)
                if not cluster_ids:
                    self._conduit_to_clusters.pop(conduit_id, None)

    def get_conduits_for_cluster(self, cluster_id: str) -> Tuple[str, ...]:
        """
        Return conduits registered in one cluster.

        Parameters
        ----------
        cluster_id:
            Cluster identifier.

        Returns
        -------
        tuple[str, ...]
            Sorted conduit ids under that cluster.
        """
        
        if not cluster_id:
            return tuple()
        with self._lock:
            return tuple(sorted(self._cluster_to_conduits.get(cluster_id, set())))

    def get_clusters_for_conduit(self, conduit_id: str) -> Tuple[str, ...]:
        """
        Return clusters that include a specific conduit.

        Parameters
        ----------
        conduit_id:
            Conduit identifier.

        Returns
        -------
        tuple[str, ...]
            Sorted cluster ids that currently contain the conduit.
        """
        
        if not conduit_id:
            return tuple()
        with self._lock:
            return tuple(sorted(self._conduit_to_clusters.get(conduit_id, set())))

    def get_cluster_objects_for_conduit(self, conduit_id: str) -> Tuple[Any, ...]:
        """
        Return live cluster objects currently associated with one conduit.

        Parameters
        ----------
        conduit_id:
            Conduit id whose cluster memberships should be resolved.

        Returns
        -------
        tuple[Any, ...]
            Live cluster objects for the conduit. Missing object references are
            skipped.
        """
        
        cluster_ids = self.get_clusters_for_conduit(conduit_id)
        clusters: List[Any] = []
        for cluster_id in cluster_ids:
            cluster = self.get_object(
                owner_kind="conduit_cluster",
                owner_id=cluster_id,
            )
            if cluster is not None:
                clusters.append(cluster)
        return tuple(clusters)

    def register_transaction(
            self,
            *,
            transaction_id: str,
            transaction_object: Any,
            transaction_type: Optional[str] = None,
            identity_keys: Optional[Iterable[Tuple[str, str]]] = None,
            scope_keys: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Register one transaction object and populate reverse indexes.

        Parameters
        ----------
        transaction_id:
            Stable id used for retrieval and deregistration.
        transaction_object:
            Live object to store.
        transaction_type:
            Optional type label used to build "_transaction_ids_by_type".
        identity_keys:
            Optional iterable of "(owner_kind, owner_id)" identifiers participating
            in the transaction.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If transaction id is empty, transaction object is "None", or malformed
            identity tuples are supplied.

        Notes
        -----
        Normalizes transaction type and identity keys before storing:
        - type is lower-cased
        - identity kinds are lower-cased and stripped
        """
        
        if not transaction_id:
            raise ValueError("transaction_id must not be empty.")
        if transaction_object is None:
            raise ValueError("transaction_object must not be None.")
        normalized_type = None
        if transaction_type is not None:
            normalized_type = transaction_type.strip().lower()
            if not normalized_type:
                raise ValueError("transaction_type must not be empty.")
        normalized_identity_keys: Set[Tuple[str, str]] = set()
        for key in identity_keys or ():
            if len(key) != 2:
                raise ValueError("identity_keys must contain (owner_kind, owner_id) pairs.")
            owner_kind, owner_id = key
            if not owner_kind or not owner_id:
                raise ValueError("identity_keys cannot contain empty values.")
            normalized_identity_keys.add((owner_kind.strip().lower(), owner_id))
        normalized_scope_keys: Set[str] = set()
        for scope_key in scope_keys or ():
            if not isinstance(scope_key, str):
                raise ValueError("scope_keys must contain string scope keys.")
            normalized_scope_key = scope_key.strip()
            if not normalized_scope_key:
                raise ValueError("scope_keys cannot contain empty values.")
            normalized_scope_keys.add(normalized_scope_key)
        with self._lock:
            self._transactions_by_id[transaction_id] = transaction_object
            self._transaction_identity_keys_by_id[transaction_id] = normalized_identity_keys
            self._transaction_scope_keys_by_id[transaction_id] = normalized_scope_keys
            if normalized_type is not None:
                self._transaction_type_by_id[transaction_id] = normalized_type
                self._transaction_ids_by_type.setdefault(normalized_type, set()).add(
                    transaction_id
                )
            for identity_key in normalized_identity_keys:
                self._transaction_ids_by_identity.setdefault(identity_key, set()).add(
                    transaction_id
                )
            for scope_key in normalized_scope_keys:
                self._transaction_ids_by_scope.setdefault(scope_key, set()).add(
                    transaction_id
                )

    def unregister_transaction(self, transaction_id: str) -> None:
        """
        Remove a transaction and all reverse transaction index entries.

        Parameters
        ----------
        transaction_id:
            Transaction id to unregister.

        Returns
        -------
        None

        Notes
        -----
        Safe when transaction id is missing. It is removed from identity and type
        indexes as well as direct storage.
        """
        
        if not transaction_id:
            return
        with self._lock:
            self._transactions_by_id.pop(transaction_id, None)
            identity_keys = self._transaction_identity_keys_by_id.pop(
                transaction_id,
                set(),
            )
            scope_keys = self._transaction_scope_keys_by_id.pop(
                transaction_id,
                set(),
            )
            for identity_key in identity_keys:
                transaction_ids = self._transaction_ids_by_identity.get(identity_key)
                if transaction_ids is not None:
                    transaction_ids.discard(transaction_id)
                    if not transaction_ids:
                        self._transaction_ids_by_identity.pop(identity_key, None)
            for scope_key in scope_keys:
                transaction_ids = self._transaction_ids_by_scope.get(scope_key)
                if transaction_ids is not None:
                    transaction_ids.discard(transaction_id)
                    if not transaction_ids:
                        self._transaction_ids_by_scope.pop(scope_key, None)
            transaction_type = self._transaction_type_by_id.pop(transaction_id, None)
            if transaction_type is not None:
                transaction_ids = self._transaction_ids_by_type.get(transaction_type)
                if transaction_ids is not None:
                    transaction_ids.discard(transaction_id)
                    if not transaction_ids:
                        self._transaction_ids_by_type.pop(transaction_type, None)

    def get_transaction(self, transaction_id: str) -> Optional[Any]:
        """
        Resolve a transaction object by id.

        Parameters
        ----------
        transaction_id:
            Transaction id.

        Returns
        -------
        Any | None
            Stored transaction object if present.
        """
        
        if not transaction_id:
            return None
        with self._lock:
            return self._transactions_by_id.get(transaction_id)

    def list_transaction_ids_for_identity(
            self,
            *,
            owner_kind: str,
            owner_id: str,
    ) -> Tuple[str, ...]:
        """
        List transaction ids associated with one identity.

        Parameters
        ----------
        owner_kind:
            Identity namespace.
        owner_id:
            Identity id.

        Returns
        -------
        tuple[str, ...]
            Sorted transaction ids.
        """
        
        if not owner_kind or not owner_id:
            return tuple()
        identity_key = (owner_kind.strip().lower(), owner_id)
        with self._lock:
            return tuple(
                sorted(self._transaction_ids_by_identity.get(identity_key, set()))
            )

    def list_live_transactions_for_identity(
            self,
            *,
            owner_kind: str,
            owner_id: str,
    ) -> Tuple[Any, ...]:
        """
        Return live transaction objects currently indexed under one identity.

        Parameters
        ----------
        owner_kind:
            Identity namespace.
        owner_id:
            Identity id within that namespace.

        Returns
        -------
        tuple[Any, ...]
            Live transaction objects currently indexed to that identity.
            Missing transaction objects are skipped.
        """
        
        transaction_ids = self.list_transaction_ids_for_identity(
            owner_kind=owner_kind,
            owner_id=owner_id,
        )
        transactions: List[Any] = []
        for transaction_id in transaction_ids:
            transaction = self.get_transaction(transaction_id)
            if transaction is not None:
                transactions.append(transaction)
        return tuple(transactions)

    def list_transaction_ids_for_type(self, transaction_type: str) -> Tuple[str, ...]:
        """
        List transaction ids associated with one transaction type.

        Parameters
        ----------
        transaction_type:
            Transaction type to resolve. It is normalized with "strip().lower()".

        Returns
        -------
        tuple[str, ...]
            Sorted transaction ids by type.
        """
        
        if not transaction_type:
            return tuple()
        normalized_type = transaction_type.strip().lower()
        with self._lock:
            return tuple(sorted(self._transaction_ids_by_type.get(normalized_type, set())))

    def list_transaction_ids_for_scope(self, scope_key: str) -> Tuple[str, ...]:
        """
        List transaction ids associated with one normalized scope key.

        Parameters
        ----------
        scope_key:
            Normalized scope key to resolve.

        Returns
        -------
        tuple[str, ...]
            Sorted transaction ids touching that scope.
        """
        if not scope_key:
            return tuple()
        normalized_scope_key = scope_key.strip()
        if not normalized_scope_key:
            return tuple()
        with self._lock:
            return tuple(sorted(self._transaction_ids_by_scope.get(normalized_scope_key, set())))

    def list_live_transactions_for_scope(self, scope_key: str) -> Tuple[Any, ...]:
        """
        Return live transaction objects currently indexed under one scope key.

        Parameters
        ----------
        scope_key:
            Normalized scope key to resolve.

        Returns
        -------
        tuple[Any, ...]
            Live transaction objects currently indexed to that scope.
        """
        transaction_ids = self.list_transaction_ids_for_scope(scope_key)
        transactions: List[Any] = []
        for transaction_id in transaction_ids:
            transaction = self.get_transaction(transaction_id)
            if transaction is not None:
                transactions.append(transaction)
        return tuple(transactions)

    def list_live_transactions_for_type(self, transaction_type: str) -> Tuple[Any, ...]:
        """
        Return live transaction objects currently indexed under one type.

        Parameters
        ----------
        transaction_type:
            Transaction type label to resolve.

        Returns
        -------
        tuple[Any, ...]
            Live transaction objects currently indexed to that type. Missing
            transaction objects are skipped.
        """
        
        transaction_ids = self.list_transaction_ids_for_type(transaction_type)
        transactions: List[Any] = []
        for transaction_id in transaction_ids:
            transaction = self.get_transaction(transaction_id)
            if transaction is not None:
                transactions.append(transaction)
        return tuple(transactions)

    def describe(self) -> Dict[str, Any]:
        """
        Build a detached diagnostic snapshot of the registry state.

        Returns
        -------
        dict[str, Any]
            Immutable mapping suitable for logs/assertions with sorted tuple values.

        Notes
        -----
        The snapshot intentionally excludes raw object references and transaction
        payloads; it returns high-level counts and indexed ids for safe telemetry.
        """
        
        with self._lock:
            return {
                "aetheric_frame_name": self._aetheric_frame_name,
                "identity_count": len(self._identities_by_key),
                "transaction_count": len(self._transactions_by_id),
                "identity_keys_by_kind": {
                    kind: tuple(sorted(keys))
                    for kind, keys in self._identity_keys_by_kind.items()
                },
                "spellbook_to_conduits": {
                    spellbook_id: tuple(sorted(conduit_ids))
                    for spellbook_id, conduit_ids in self._spellbook_to_conduits.items()
                },
                "transaction_ids_by_scope": {
                    scope_key: tuple(sorted(transaction_ids))
                    for scope_key, transaction_ids in self._transaction_ids_by_scope.items()
                },
                "provider_to_borrowers": {
                    provider_id: tuple(sorted(borrower_ids))
                    for provider_id, borrower_ids in self._provider_to_borrowers.items()
                },
                "cluster_to_conduits": {
                    cluster_id: tuple(sorted(conduit_ids))
                    for cluster_id, conduit_ids in self._cluster_to_conduits.items()
                },
            }
