from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.creations.spellspace_creations import (
    Creations,
)
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)


class ConduitCreations(Creations):
    """
    Conduit-owned live creation registry.

    Purpose:
        Extend the scoped `Creations` base with conduit-specific spellspace
        stack ownership and mixed-scope extraction/restore behavior.

    Contract:
        - Inherits non-spellspace singleton/many storage from `Creations`.
        - Adds spellspace bucket storage inside the same registries until the
          runtime is fully rewired onto `SpellSpaceCreations`.
        - Owns one thread-local spellspace stack for the conduit runtime.
        - Cleanup clears both the scoped creation registries and the conduit's
          spellspace stack reference.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ["_spellspace_stack"]

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
        if spellspace_stack is None:
            raise ValueError("spellspace_stack must not be None.")
        super().__init__(
            owner_conduit_id=conduit_id,
            id=conduit_id,
        )
        self._spellspace_stack: SpellSpaceThreadState = spellspace_stack

    def cleanup(self) -> None:
        """
        Dispose tracked disposable entries and release owned conduit state.

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
        del self._spellspace_stack
        del self._owner_conduit_id
        del self._id
        del self._lock

        if errors:
            raise ExceptionGroup("Errors occurred during cleaning", errors)

    def extract_spell_creations(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Remove and return all creations for one spell id across conduit and spellspace scopes.
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
        if bucket is None:
            return None
        return bucket.get(spell_id)

    def get_active_spellspace(self) -> Any:
        """
        Return the current active spellspace for this creations owner, if any.
        """
        return self._spellspace_stack.get_active()

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
