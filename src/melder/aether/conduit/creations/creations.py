from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable

StoredDisposalEntry = Tuple[object, List[str]]


class Creations(Cleanable):
    """
    Scoped live creation registry.

    Purpose:
        Own the live object store for exactly one scoped creations owner
        without conduit spellspace stacks or spellspace-id bucket indirection.

    Contract:
        - One `Creations` instance belongs to one concrete scope id.
        - `_creations` is the authoritative live-object registry for that scope.
        - `_disposable_creations` is cleanup-only metadata and is never used
          for normal runtime retrieval.
        - Unique entries use `spell_id -> object`.
        - Many entries use `spell_id -> list[object]`.
        - Disposal metadata mirrors only entries that declared disposal
          methods:
          - unique: `spell_id -> (object, disposal_methods)`
          - many: `spell_id -> list[(object, disposal_methods)]`
        - Cleanup and reusable clearing are explicit, idempotent, and aggregate
          disposal failures.

    Owned State:
        `_owner_conduit_id`, a stable `_id`, one `RLock`, and the two registries
        (`_creations`, `_disposable_creations`).

    Threading:
        One instance `RLock` guards both registries. Reads and writes race
        freely under free-threaded 3.14t, so the lock is not optional.

    Lifecycle / Cleanup:
        Idempotent. Cleanup runs the declared disposal methods and AGGREGATES
        failures rather than stopping at the first one - a single badly behaved
        object must not strand the rest of the scope's teardown, so callers may
        see an ExceptionGroup.

        Disposal runs in REVERSE CREATION ORDER, newest entry first, including
        within a `many` bucket. Resolution registers a dependency before the
        dependent that holds it, so forward teardown would dispose the
        dependency while a dependent's own disposal method may still need it.
        This covers ordering within ONE scope; ordering between scopes is the
        conduit cleanup cascade's job.

    Registration:
        MELDER KERNEL. The one subclass, `ConduitCreations`, is melder-internal and
        constructed only inside `Conduit.__init__`; there is no injection seam.
        `ClusterCreations` does NOT extend this class - it extends `Cleanable`
        directly.

    Subsystem Context:
        The storage layer beneath `Meld`. Meld decides WHICH store an
        `Existence` routes to; this class is what one such store actually is.
        `ConduitCreations` specializes it for conduit/root scope, and the two
        meld doors read these stores rather than owning object lifetime
        themselves.

    System Context:
        The two-registry split is the important design choice and it is easy to
        misread as duplication. `_creations` is the AUTHORITATIVE live-object
        registry and is the only thing consulted during resolution;
        `_disposable_creations` is cleanup-only metadata that mirrors just those
        entries which declared disposal methods. Keeping them apart means the
        resolution hot path never pays for disposal bookkeeping, and it means
        an object without disposal methods costs nothing extra to track.
        This is also why the store is generic over scope rather than
        conduit-specific: the same structure serves conduit, root, cluster,
        lineage, and spellspace scopes, so a lifetime is expressed by WHICH
        instance holds the object, not by a different storage shape per mode.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Scoped live creation registry. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_owner_conduit_id",
        "_id",
        "_lock",
        "_creations",
        "_disposable_creations",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            id: str,
    ) -> None:
        """
        Initialize one scoped creation registry.

        Purpose:
            Create the smallest live-object store that can own one scope's
            runtime creations without any ambient spellspace-stack or
            conduit-lineage lookup rules.

        Contract:
            - `owner_conduit_id` identifies the conduit that owns the scope.
            - `id` identifies the concrete scope itself (conduit id,
              spellspace id, or another explicit owner id).
            - Initializes one live registry and one detached cleanup-metadata
              registry.
            - Does not pre-populate any spell buckets.

        Args:
            owner_conduit_id:
                Stable id of the conduit that owns the scope.
            id:
                Stable id of the owning scope.

        Raises:
            ValueError:
                If either identifier is empty.

        Returns:
            None.
        """
        super().__init__()
        if not owner_conduit_id:
            raise ValueError("owner_conduit_id must not be empty.")
        if not id:
            raise ValueError("id must not be empty.")

        self._owner_conduit_id: str = owner_conduit_id
        self._id: str = id
        self._lock = RLock()
        self._creations: Dict[str, Any] = {}
        self._disposable_creations: Dict[str, Any] = {}
        # Note: resolution-store selection for broad-lived existences
        # (`unique_per_conduit_lineage` lineage root, `unique_per_conduit_cluster`
        # elected-leader store) lives on the meld front doors
        # (`ConduitMeld` / `SpellSpaceMeld`), not on this store. `Creations` is a
        # pure scoped live-object bucket and intentionally holds no pointer to
        # any other `Creations`; the resolving door is handed the target store
        # at runtime by the meld instead of dereferencing it off the caller's
        # store.

    def cleanup(self) -> None:
        """
        Dispose tracked entries and permanently retire this registry.

        Contract:
            - Idempotent.
            - Detaches live and disposable registries before disposal work.
            - Uses `_disposable_creations` only for explicit teardown work.
            - Raises `ExceptionGroup` after best-effort disposal attempts.
            - Drops the live field surface after cleanup so later use fails
              honestly instead of reading stale state.

        Threading:
            - Performs the detach step under `_lock`.
            - Disposal work happens after detach so callers cannot keep racing
              the live registries while cleanup is executing.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            disposable_creations = self._disposable_creations
            creations = self._creations
            self._creations = {}
            self._disposable_creations = {}

        try:
            errors = self._dispose_disposable_registry(disposable_creations)
        except Exception as exc:
            errors = [exc]
        disposable_creations.clear()
        creations.clear()

        del self._creations
        del self._disposable_creations
        del self._owner_conduit_id
        del self._id
        del self._lock

        if errors:
            raise ExceptionGroup("Errors occurred during cleaning", errors)

    def _attempt_cleanup(self, entry: StoredDisposalEntry) -> Optional[Exception]:
        """
        Attempt explicit disposal for one tracked entry.

        Args:
            entry:
                `(object, disposal_method_names)` tuple.

        Returns:
            Optional[Exception]:
                Wrapped disposal error when disposal fails, otherwise `None`.
        """
        item, method_names = entry
        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
            except Exception as ex:
                return RuntimeError(
                    f"Failed to dispose object {item} using method '{method_name}': {ex}"
                )
        return None

    def _dispose_disposable_registry(
            self,
            disposable_registry: Dict[str, Any],
    ) -> List[Exception]:
        """
        Dispose every entry recorded in one detached disposable registry.

        Args:
            disposable_registry:
                Detached cleanup-only metadata mapping.

        Ordering:
            REVERSE CREATION ORDER. Entries are disposed newest-first, and the
            same rule applies inside a `many` bucket. This matters because
            resolution builds a dependency before the dependent that holds it,
            so the dependency is registered FIRST; walking forward would tear it
            down while a dependent's own disposal method may still reach for it.
            No ordering structure is needed to achieve this - `_disposable_creations`
            is a plain dict, dict iteration is insertion-ordered by language
            guarantee, and insertion happens at creation time, so the registry
            already IS the creation-order record.

            This orders teardown WITHIN one scope only. Ordering BETWEEN scopes
            (lesser conduit before root, narrower existence before broader) is
            owned by the conduit cleanup cascade, not by this method.

        Returns:
            List[Exception]:
                Collected disposal failures, in the order the failures occurred.
        """
        errors: List[Exception] = []
        for value in reversed(disposable_registry.values()):
            if isinstance(value, tuple):
                maybe_error = self._attempt_cleanup(value)
                if maybe_error:
                    errors.append(maybe_error)
                continue
            if isinstance(value, list):
                for entry in reversed(value):
                    maybe_error = self._attempt_cleanup(entry)
                    if maybe_error:
                        errors.append(maybe_error)
        return errors

    def add_creation(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one scoped singleton creation.

        Contract:
            - Stores the live object in `_creations`.
            - Stores cleanup metadata in `_disposable_creations` only when
              disposal methods were declared.
            - Rejects duplicate keys across both registries.
            - Treats the stored object itself as the authoritative runtime
              payload; there is no `Creation.value` wrapper in the live store.

        Returns:
            None.
        """
        if key in self._creations or key in self._disposable_creations:
            raise ValueError(f"Key {key} already exists in creations.")

        self._creations[key] = item
        if has_disposal_methods:
            self._disposable_creations[key] = (
                item,
                list(disposal_methods) if disposal_methods else [],
            )

    def add_many_creations(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one creation into the scoped `many` list for a spell id.

        Contract:
            - Appends the live object into `_creations[key]`.
            - Appends cleanup metadata into `_disposable_creations[key]` only
              when disposal methods were declared.
            - Rejects collisions with non-list slots.
            - Preserves insertion order inside both the live many bucket and
              the matching disposable metadata bucket.
            - First-use bucket creation and both appends are atomic with
              respect to competing resolutions (BUG-073, 2026-07-17 audit):
              the whole live+disposable mutation runs under `_lock`, so two
              threads first-resolving the same key can never overwrite each
              other's bucket and strand a successfully returned creation
              outside lifetime and disposal tracking.

        Threading:
            - Runs under `_lock` (re-entrant, shared with extract/restore/
              clear); every successfully returned managed creation is
              represented in both registries once this method returns.

        Returns:
            None.
        """
        with self._lock:
            live_value = self._creations.get(key)
            if live_value is None:
                self._creations[key] = []
                live_value = self._creations[key]
            if not isinstance(live_value, list):
                raise ValueError(
                    f"Key {key} already exists in creations with non-list slot."
                )
            live_value.append(item)

            if not has_disposal_methods:
                return

            disposable_value = self._disposable_creations.get(key)
            if disposable_value is None:
                self._disposable_creations[key] = []
                disposable_value = self._disposable_creations[key]
            if not isinstance(disposable_value, list):
                raise ValueError(
                    f"Key {key} already exists in disposable creations with non-list slot."
                )
            disposable_value.append(
                (
                    item,
                    list(disposal_methods) if disposal_methods else [],
                )
            )

    def get_creation(self, spell_id: str) -> Optional[Any]:
        """
        Return one scoped live object by spell id.

        Contract:
            - Reads only `_creations`.
            - Never consults `_disposable_creations`.
            - Returns the stored object directly.
        """
        return self._creations.get(spell_id)

    def extract_spell_creations(
            self,
            spell_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Remove and return all locally owned creations for one spell id.

        Contract:
            - Extracts only this scoped store's local state.
            - Preserves enough metadata for later restore.
            - Supports both singleton and `many` storage shapes.
            - Does not reach into external owners or adjacent scopes.
            - Returns raw stored objects plus disposal metadata, not a richer
              wrapper object.

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        """
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            live_value = self._creations.get(spell_id)
            disposable_value = self._disposable_creations.get(spell_id)

            if isinstance(live_value, list):
                live_many = self._creations.pop(spell_id)
                disposable_many = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, list)
                    else None
                )
                for index, stored_value in enumerate(live_many):
                    entry = {
                        "scope": "many",
                        "disposable": disposable_many is not None,
                        "stored": stored_value,
                    }
                    if disposable_many is not None:
                        entry["disposal_methods"] = list(disposable_many[index][1])
                    extracted.append(entry)
            elif live_value is not None and not isinstance(live_value, dict):
                stored_value = self._creations.pop(spell_id)
                disposable_entry = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, tuple)
                    else None
                )
                entry = {
                    "scope": "unique",
                    "disposable": disposable_entry is not None,
                    "stored": stored_value,
                }
                if disposable_entry is not None:
                    entry["disposal_methods"] = list(disposable_entry[1])
                extracted.append(entry)

        return extracted

    def restore_spell_creations(
            self,
            spell_id: str,
            creations: List[Dict[str, Any]],
    ) -> None:
        """
        Restore locally owned creations previously extracted for one spell id.

        Contract:
            - Rebuilds this scoped store from the extracted payload only.
            - Replaces any current local state for the spell id.
            - Restores both live entries and disposal metadata.
            - Raises when the payload does not match the local slot shape.
            - Restores the same raw object references that were extracted; it
              does not clone or rehydrate them.

        Returns:
            None.
        """
        if not creations:
            return

        with self._lock:
            live_value = self._creations.get(spell_id)
            if live_value is not None:
                self._creations.pop(spell_id)
            self._disposable_creations.pop(spell_id, None)

            for entry in creations:
                scope = entry["scope"]
                is_disposable = entry["disposable"]
                stored_value = entry["stored"]
                disposal_methods = entry.get("disposal_methods")

                if scope == "unique":
                    existing = self._creations.get(spell_id)
                    if isinstance(existing, dict):
                        raise RuntimeError(
                            f"Cannot restore unique creation for spell '{spell_id}' into non-singleton slot."
                        )
                    self._creations[spell_id] = stored_value
                    if is_disposable:
                        self._disposable_creations[spell_id] = (
                            stored_value,
                            list(disposal_methods) if disposal_methods else [],
                        )
                    continue

                if scope == "many":
                    existing = self._creations.get(spell_id)
                    if existing is None:
                        self._creations[spell_id] = []
                        existing = self._creations[spell_id]
                    if not isinstance(existing, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    existing.append(stored_value)
                    if is_disposable:
                        disposable_many = self._disposable_creations.get(spell_id)
                        if disposable_many is None:
                            self._disposable_creations[spell_id] = []
                            disposable_many = self._disposable_creations[spell_id]
                        if not isinstance(disposable_many, list):
                            raise RuntimeError(
                                f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                            )
                        disposable_many.append(
                            (
                                stored_value,
                                list(disposal_methods) if disposal_methods else [],
                            )
                        )
                    continue

                raise RuntimeError(
                    f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                )

    def clear_all(self) -> None:
        """
        Dispose and remove all scoped entries without destroying this object.

        Contract:
            - Reusable clear for scope cleanup or pooling flows.
            - Detaches live and disposable registries before disposal work.
            - Raises `ExceptionGroup` after best-effort disposal attempts.
            - Leaves this `Creations` instance reusable after the clear
              completes.

        Returns:
            None.
        """
        with self._lock:
            if not self._creations and not self._disposable_creations:
                return
            live_creations = self._creations
            disposable_creations = self._disposable_creations
            self._creations = {}
            self._disposable_creations = {}

        errors = self._dispose_disposable_registry(disposable_creations)
        live_creations.clear()
        disposable_creations.clear()

        if errors:
            raise ExceptionGroup("Errors occurred during creations clear", errors)

    def reset_for_pool(self) -> None:
        """
        Clear all live scoped state without destroying this manager.

        Contract:
            - Keeps the same observable result as `clear_all()` for callers.
            - Uses a fast path when no disposable metadata is present:
              clear only the live registry under lock and return.
            - Falls back to the full detachable disposal flow when disposable
              cleanup work is required.

        Returns:
            None.
        """
        with self._lock:
            if not self._creations and not self._disposable_creations:
                return
            if not self._disposable_creations:
                self._creations.clear()
                return
        self.clear_all()

    def reset_for_pool_unlocked(self) -> None:
        """
        Clear all live scoped state without taking the instance lock.

        Purpose:
            Provide the managed spellspace exit lane with a lock-free scope
            clear, removing the last per-cycle lock acquisition from the
            `with conduit.enter_spellspace():` hot path.

        Contract:
            - Same observable result as `reset_for_pool()` for the caller.
            - Caller-guaranteed thread confinement is REQUIRED: this method
              may only be called when the owning scope object is confined to
              the calling thread, as on the managed spellspace exit lane
              (pool deque hand-off in, per-thread stack while live,
              LIFO-validated exit out; the pool deque ops are the cross-thread
              synchronization points). Calling it on a store that other
              threads may be reading or mutating concurrently is a caller
              contract violation.
            - Disposal work stays safe: when disposable metadata is present,
              this method falls back to the fully locked `clear_all()` flow,
              because explicit teardown of user objects is never run
              lock-free.

        Threading:
            - No lock is taken on the fast (no-disposables) path by design;
              see the confinement contract above.

        Returns:
            None.
        """
        if not self._disposable_creations:
            creations = self._creations
            if creations:
                creations.clear()
            return
        self.clear_all()

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this scoped registry.

        Returns:
            str: Conduit id that owns the scope represented by this registry.
        """
        return self._owner_conduit_id

    @property
    def id(self) -> str:
        """
        Return the stable owner scope id for this registry.

        Returns:
            str: Concrete scope id for this registry (for example a conduit id
            or spellspace id).
        """
        return self._id
