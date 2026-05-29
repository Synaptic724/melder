from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

StoredDisposalEntry = Tuple[object, List[str]]


class Creations(Cleanable):
    """
    Spellspace-local live creation registry.

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

    Ownership:
        - The owner scope id is fixed at construction time.
        - The owner conduit id is retained only as metadata for higher-level
          coordination and diagnostics.
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

    def clear_all(self) -> None:
        """
        Dispose and remove all scoped entries without destroying this object.

        Contract:
            - Reusable clear for scope cleanup or pooling flows.
            - Detaches live and disposable registries before disposal work.
            - Raises `ExceptionGroup` after best-effort disposal attempts.
        """
        with self._lock:
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
        """
        return self._owner_conduit_id

    @property
    def id(self) -> str:
        """
        Return the stable owner scope id for this registry.
        """
        return self._id
