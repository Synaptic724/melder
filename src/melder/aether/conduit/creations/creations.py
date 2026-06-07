from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
                return None
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

        Returns:
            List[Exception]:
                Collected disposal failures.
        """
        errors: List[Exception] = []
        for value in disposable_registry.values():
            if isinstance(value, tuple):
                maybe_error = self._attempt_cleanup(value)
                if maybe_error:
                    errors.append(maybe_error)
                continue
            if isinstance(value, list):
                for entry in value:
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
        """
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
            Alias for `clear_all()` so future pooling can reuse the same
            cleanup surface.
        """
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
