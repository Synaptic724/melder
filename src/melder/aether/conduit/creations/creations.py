from threading import RLock
from typing import List, Optional, Dict, Any, ClassVar, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

StoredDisposalEntry = Tuple[object, List[str]]


class Creations(Cleanable):
    """
    Conduit-owned live creation registry.

    Purpose:
        Own the live object store used by meld reuse while keeping explicit
        disposal metadata off the hot lookup path.

    Contract:
        - `_creations` is the only authoritative live-object registry.
        - `_disposable_creations` is cleanup-only metadata and is never used for
          normal runtime retrieval.
        - Non-spellspace unique entries use `spell_id -> object`.
        - Non-spellspace many entries use `spell_id -> list[object]`.
        - Spellspace entries use `spellspace_id -> dict[spell_id, object]`.
        - Disposal metadata mirrors only entries that declared disposal methods:
          - unique: `spell_id -> (object, disposal_methods)`
          - many: `spell_id -> list[(object, disposal_methods)]`
          - spellspace: `spellspace_id -> dict[spell_id, (object, disposal_methods)]`
        - Cleanup is explicit, idempotent, and aggregates disposal failures.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_owner_conduit_id",
        "_id",
        "_lock",
        "_creations",
        "_disposable_creations",
        "_spellspace_stack",
    ]

    def __init__(
            self,
            *,
            conduit_id: str,
            spellspace_stack: SpellSpaceThreadState,
    ) -> None:
        """
        Initialize the conduit-local creation registry.

        Args:
            conduit_id:
                Stable id of the conduit that owns this registry.
            spellspace_stack:
                Thread-local active spellspace stack for this creations owner.

        Raises:
            ValueError:
                If `conduit_id` is empty or `spellspace_stack` is missing.
        """
        super().__init__()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if spellspace_stack is None:
            raise ValueError("spellspace_stack must not be None.")

        self._owner_conduit_id: str = conduit_id
        self._id: str = conduit_id
        self._lock = RLock()
        self._creations: Dict[str, Any] = {}
        self._disposable_creations: Dict[str, Any] = {}
        self._spellspace_stack: SpellSpaceThreadState = spellspace_stack

    def cleanup(self) -> None:
        """
        Dispose tracked disposable entries and release owned state.

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
            live_creations = self._creations
            disposable_creations = self._disposable_creations
            self._creations = {}
            self._disposable_creations = {}

        try:
            errors = self._dispose_disposable_registry(disposable_creations)
        except Exception as exc:
            errors = [exc]
        live_creations.clear()
        disposable_creations.clear()

        del self._creations
        del self._disposable_creations
        del self._spellspace_stack
        del self._owner_conduit_id
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

    def _dispose_disposable_registry(self, disposable_registry: Dict[str, Any]) -> List[Exception]:
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
                continue
            if isinstance(value, dict):
                for entry in value.values():
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
        Register one non-spellspace singleton creation.

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
        Register one creation into the `many` storage list for a spell id.

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
                f"Key {key} already exists in creations with non-list slot."
            )
        disposable_value.append(
            (
                item,
                list(disposal_methods) if disposal_methods else [],
            )
        )

    def extract_spell_creations(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Remove and return all creations for one spell id across all scopes.

        Returns:
            List[Dict[str, Any]]:
                Serialized stored-entry payloads suitable for
                `restore_spell_creations`.
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

            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                stored_value = bucket.pop(spell_id)
                disposable_bucket = self._disposable_creations.get(spellspace_id)
                disposable_entry = None
                if isinstance(disposable_bucket, dict):
                    disposable_entry = disposable_bucket.pop(spell_id, None)
                    if not disposable_bucket:
                        del self._disposable_creations[spellspace_id]
                entry = {
                    "scope": "spellspace",
                    "spellspace_id": spellspace_id,
                    "disposable": disposable_entry is not None,
                    "stored": stored_value,
                }
                if disposable_entry is not None:
                    entry["disposal_methods"] = list(disposable_entry[1])
                extracted.append(entry)
                if not bucket:
                    del self._creations[spellspace_id]

        return extracted

    def restore_spell_creations(self, spell_id: str, creations: List[Dict[str, Any]]) -> None:
        """
        Restore creations previously extracted for one spell id.
        """
        if not creations:
            return

        with self._lock:
            live_value = self._creations.get(spell_id)
            if live_value is not None and not isinstance(live_value, dict):
                self._creations.pop(spell_id)
            self._disposable_creations.pop(spell_id, None)

            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id in bucket:
                    bucket.pop(spell_id)
                    if not bucket:
                        del self._creations[spellspace_id]
            for spellspace_id, bucket in list(self._disposable_creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id in bucket:
                    bucket.pop(spell_id)
                    if not bucket:
                        del self._disposable_creations[spellspace_id]

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

                if scope == "spellspace":
                    spellspace_id = entry["spellspace_id"]
                    bucket = self._creations.get(spellspace_id)
                    if bucket is None:
                        self._creations[spellspace_id] = {}
                        bucket = self._creations[spellspace_id]
                    if not isinstance(bucket, dict):
                        raise RuntimeError(
                            f"Cannot restore spellspace creation for spellspace '{spellspace_id}' into non-dict slot."
                        )
                    bucket[spell_id] = stored_value
                    if is_disposable:
                        disposable_bucket = self._disposable_creations.get(spellspace_id)
                        if disposable_bucket is None:
                            self._disposable_creations[spellspace_id] = {}
                            disposable_bucket = self._disposable_creations[spellspace_id]
                        if not isinstance(disposable_bucket, dict):
                            raise RuntimeError(
                                f"Cannot restore spellspace creation for spellspace '{spellspace_id}' into non-dict slot."
                            )
                        disposable_bucket[spell_id] = (
                            stored_value,
                            list(disposal_methods) if disposal_methods else [],
                        )
                    continue

                raise RuntimeError(
                    f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                )

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Optional[Any]:
        """
        Return one spellspace-scoped live object by spellspace id and spell id.
        """
        bucket = self._creations.get(spellspace_id)
        if not isinstance(bucket, dict):
            return None
        return bucket.get(spell_id)

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this creations manager.
        """
        return self._owner_conduit_id

    def get_active_spellspace(self) -> Any:
        """
        Return the current active spellspace for this creations owner, if any.
        """
        return self._spellspace_stack.get_active()

    def get_creation(self, spell_id: str) -> Optional[Any]:
        """
        Return one non-spellspace retained object by spell id, if present.
        """
        entry = self._creations.get(spell_id)
        if entry is not None and not isinstance(entry, dict) and not isinstance(entry, list):
            return entry
        return None

    def register_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one creation into a spellspace bucket.
        """
        live_bucket = self._creations.get(spellspace_id)
        if live_bucket is None:
            self._creations[spellspace_id] = {}
            live_bucket = self._creations[spellspace_id]
        if not isinstance(live_bucket, dict):
            raise ValueError(
                f"Key {spellspace_id} already exists in creations with non-spellspace scope."
            )
        if spell_id in live_bucket:
            raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
        live_bucket[spell_id] = item

        if not has_disposal_methods:
            return

        disposable_bucket = self._disposable_creations.get(spellspace_id)
        if disposable_bucket is None:
            self._disposable_creations[spellspace_id] = {}
            disposable_bucket = self._disposable_creations[spellspace_id]
        if not isinstance(disposable_bucket, dict):
            raise ValueError(
                f"Key {spellspace_id} already exists in disposable creations with non-spellspace scope."
            )
        disposable_bucket[spell_id] = (
            item,
            list(disposal_methods) if disposal_methods else [],
        )

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Dispose and remove all entries for one spellspace bucket.
        """
        with self._lock:
            live_bucket = self._creations.pop(spellspace_id, None)
            if live_bucket is not None and not isinstance(live_bucket, dict):
                self._creations[spellspace_id] = live_bucket
                return
            disposable_bucket = self._disposable_creations.pop(spellspace_id, None)
            if disposable_bucket is not None and not isinstance(disposable_bucket, dict):
                raise RuntimeError(
                    f"Disposable spellspace slot '{spellspace_id}' is not a spellspace bucket."
                )

        if disposable_bucket is None:
            return

        errors: List[Exception] = []
        for entry in disposable_bucket.values():
            maybe_error = self._attempt_cleanup(entry)
            if maybe_error:
                errors.append(maybe_error)

        if live_bucket is not None:
            live_bucket.clear()
        disposable_bucket.clear()

        if errors:
            raise ExceptionGroup("Errors occurred during spellspace cleanup", errors)

    def reset_for_pool(self) -> None:
        """
        Clear all live creation state without destroying this manager.
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
            raise ExceptionGroup("Errors occurred during pooled reset", errors)

    def reset_non_spellspace_for_pool(self) -> None:
        """
        Clear only non-spellspace creation state without touching spellspace buckets.
        """
        with self._lock:
            plain_non_spellspace: Dict[str, Any] = {}
            disposable_non_spellspace: Dict[str, Any] = {}

            for key, item in list(self._creations.items()):
                if isinstance(item, dict):
                    continue
                plain_non_spellspace[key] = self._creations.pop(key)
            for key, item in list(self._disposable_creations.items()):
                if isinstance(item, dict):
                    continue
                disposable_non_spellspace[key] = self._disposable_creations.pop(key)

        errors = self._dispose_disposable_registry(disposable_non_spellspace)
        plain_non_spellspace.clear()
        disposable_non_spellspace.clear()

        if errors:
            raise ExceptionGroup(
                "Errors occurred during pooled non-spellspace reset",
                errors,
            )
