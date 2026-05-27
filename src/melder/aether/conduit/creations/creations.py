from collections import deque
from threading import RLock
from typing import List, Optional, Dict, Any, ClassVar, Tuple

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

StoredDisposalEntry = Tuple[object, List[str]]

# TODO: Narrow this manager's public surface so storage/disposal internals are
# not the default interface exposed to the rest of the conduit runtime.

class Creations(Cleanable):
    """
    Conduit-owned registry for live creation objects and their disposal state.

    `Creations` is the runtime store behind meld reuse. It tracks live objects
    under the spell's lifecycle contract, keeps non-disposable retained entries
    as raw refs, keeps explicit-disposal entries in a separate storage surface,
    and owns the ordered cleanup stacks that are drained when the conduit tears
    down.

    Responsibilities:
    - store plain retained entries and disposal-tracked entries separately
    - preserve lifecycle semantics for singleton, many, and spellspace routes
    - record disposal ordering through global and spellspace-local stacks
    - support extraction/restoration workflows used by ownership transfer

    Contract:
    - cleanup is idempotent and drains disposal stacks before references are
      nulled
    - disposal method order comes from the stored disposal entry metadata
    - cleanup errors are aggregated and raised only after teardown work
      finishes
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_owner_conduit_id",
        "_id",
        "_lock",
        "_disposal_stack",
        "_spellspace_disposal_stacks",
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
        Purpose:
            Initialize the conduit creations registry.

        Contract:
            - Owns one shared plain creations map and one shared disposable
              creations map for non-spellspace and spellspace entries.
            - Owns one global disposal stack and per-spellspace disposal stacks.

        Args:
            conduit_id:
                Stable id of the conduit that owns this Creations manager.
            spellspace_stack:
                Context-local stack used to identify the currently active
                spellspace for this creations owner.

        Returns:
            None.

        Raises:
            ValueError:
                If `conduit_id` is empty or `spellspace_stack` is missing.
        """
        super().__init__()
        self._owner_conduit_id: str = conduit_id
        self._id: str = conduit_id
        self._spellspace_stack: SpellSpaceThreadState = spellspace_stack

        self._lock = RLock()
        self._disposal_stack: deque = deque()
        self._spellspace_disposal_stacks: Dict[str, deque] = {}

        # Plain retained storage:
        # - non-spellspace entries are keyed by spell_id
        # - spellspace entries are keyed by spellspace_id and hold nested buckets
        self._creations: Dict[str, Any] = {}
        # Disposal-tracked retained storage mirrors the same key layout but
        # stores `(object, disposal_method_names)` tuples instead of raw refs.
        self._disposable_creations: Dict[str, Any] = {}


    #region Destructor
    def cleanup(self) -> None:
        """
        Purpose:
            Dispose all tracked creations and teardown owned references.

        Contract:
            - Idempotent.
            - Drains global disposal stack first, then spellspace disposal stacks.
            - Clears all internal containers and nulls owned references.
            - Raises aggregated disposal failures after teardown.

        Returns:
            None.

        Raises:
            ExceptionGroup:
                If one or more disposal operations fail.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            errors: List[Exception] = []

            # Single try/except around the whole sequence (per request)
            try:
                errors.extend(self._drain_disposal_stack())
                for spellspace_id in list(self._spellspace_disposal_stacks.keys()):
                    errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
            except Exception as e:
                # Fatal exception in the sequence (unexpected); record and continue teardown
                errors.append(e)

            # Null internal refs last
            self._creations.clear()
            self._disposable_creations.clear()
            self._spellspace_disposal_stacks.clear()
            self._disposal_stack.clear()

            del self._creations
            del self._disposable_creations
            del self._spellspace_disposal_stacks
            del self._spellspace_stack
            del self._owner_conduit_id
            del self._disposal_stack

            if errors:
                raise ExceptionGroup("Errors occurred during cleaning", errors)

    def _cleanup_spellspace_instances(self) -> List[Exception]:
        """
        Purpose:
            Dispose all spellspace-scoped entries.

        Contract:
            - Drains each spellspace disposal stack before clearing bucket entries.
            - Clears spellspace stacks after bucket teardown.

        Returns:
            List[Exception]:
                Collected disposal errors.
        """
        errors: List[Exception] = []
        for spellspace_id, bucket in list(self._creations.items()):
            if not isinstance(bucket, dict):
                continue
            bucket.clear()
            del self._creations[spellspace_id]
        for spellspace_id, bucket in list(self._disposable_creations.items()):
            if not isinstance(bucket, dict):
                continue
            errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
            bucket.clear()
            del self._disposable_creations[spellspace_id]
        self._spellspace_disposal_stacks.clear()
        return errors

    def _attempt_cleanup(self, entry: StoredDisposalEntry) -> Optional[Exception]:
        """
        Attempt disposal for one entry using its configured method order.

        This helper is the core disposal-policy interpreter. It does not guess
        or probe multiple protocols beyond the configured method-name list.
        The first configured method that exists is called; if it raises, the
        error is wrapped and returned for later aggregation.

        Args:
            entry:
                `(object, disposal_method_names)` tuple whose object may expose
                one of the configured disposal methods.

        Returns:
            Optional[Exception]: Wrapped disposal error when the chosen cleanup
            method fails, otherwise `None`.
        """
        item, method_names = entry
        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
                return None
            except Exception as ex:
                return RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")

        return None

    def _push_disposal_creation(self, entry: StoredDisposalEntry) -> None:
        """
        Register one creation on the global disposal stack.

        Only entries that actually declare disposal methods are pushed, so the
        stack represents "must attempt explicit disposal" work rather than every
        live object in the registry.
        """
        self._disposal_stack.appendleft(entry)

    def _push_spellspace_disposal_creation(self, spellspace_id: str, entry: StoredDisposalEntry) -> None:
        """
        Register one creation on its spellspace-local disposal stack.

        Spellspace-scoped creations use a separate stack so teardown can drain
        each spellspace bucket deterministically without mixing it into the
        global conduit-level disposal order.
        """
        stack = self._spellspace_disposal_stacks.setdefault(spellspace_id, deque())
        stack.appendleft(entry)

    def _remove_disposal_creation(self, entry: StoredDisposalEntry) -> None:
        """
        Remove one creation from the global disposal stack if present.

        This is primarily used by extraction/transfer flows that move creations
        out of the registry and need the disposal bookkeeping to stay aligned
        with the moved objects.
        """
        filtered_items = [
            item
            for item in self._disposal_stack
            if item is not entry
        ]
        self._disposal_stack = deque(filtered_items)

    def _remove_spellspace_disposal_creation(self, spellspace_id: str, entry: StoredDisposalEntry) -> None:
        """
        Remove one creation from a spellspace-local disposal stack if present.

        This is the spellspace-scoped counterpart to `_remove_disposal_creation`
        and keeps per-spellspace disposal bookkeeping aligned with extraction or
        bucket-clearing flows.
        """
        stack = self._spellspace_disposal_stacks.get(spellspace_id)
        if not stack:
            return
        filtered_items = [
            item
            for item in stack
            if item is not entry
        ]
        self._spellspace_disposal_stacks[spellspace_id] = deque(filtered_items)

    def _drain_disposal_stack(self) -> List[Exception]:
        """
        Drain the global disposal stack in LIFO order.

        The stack is drained front-to-back because creations are pushed with
        `appendleft`, making the newest disposal candidate run first during
        teardown. Disposal errors are collected rather than raised immediately
        so the remaining cleanup work still executes.
        """
        errors: List[Exception] = []
        while self._disposal_stack:
            entry = self._disposal_stack.popleft()
            maybe_error = self._attempt_cleanup(entry)
            if maybe_error:
                errors.append(maybe_error)
        return errors

    def _drain_spellspace_disposal_stack(self, spellspace_id: str) -> List[Exception]:
        """
        Drain one spellspace-local disposal stack in LIFO order.

        This keeps spellspace teardown deterministic and self-contained while
        using the same error-collection model as the global disposal stack.
        """
        errors: List[Exception] = []
        stack = self._spellspace_disposal_stacks.get(spellspace_id)
        if not stack:
            return errors
        while stack:
            entry = stack.popleft()
            maybe_error = self._attempt_cleanup(entry)
            if maybe_error:
                errors.append(maybe_error)
        return errors


    #endregion Destructor
    def add_creation(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Purpose:
            Register one non-spellspace singleton creation for a spell id.

        Contract:
            - Inserts one retained entry under `key`.
            - Non-disposable entries are stored as raw object refs in
              `_creations`.
            - Disposal-tracked entries are stored as
              `(object, disposal_method_names)` tuples in
              `_disposable_creations`.
            - Rejects duplicate keys regardless of singleton lifetime kind.
            - Pushes to the disposal stack only when disposal methods are declared.

        Args:
            key:
                Spell id used as the singleton slot key.
            item:
                Resolved instance to wrap and register.
            has_disposal_methods:
                True when this spell declared disposal methods.
            disposal_methods:
                Ordered disposal method names for the creation.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the Creations manager is already cleaned.
            ValueError:
                If `key` already exists in the shared creations map.
        """
        
        if key in self._creations or key in self._disposable_creations:
            raise ValueError(f"Key {key} already exists in creations.")
        if has_disposal_methods:
            disposable_entry: StoredDisposalEntry = (
                item,
                list(disposal_methods) if disposal_methods else [],
            )
            self._disposable_creations[key] = disposable_entry
            self._push_disposal_creation(disposable_entry)
            return
        self._creations[key] = item

    def add_many_creations(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Purpose:
            Register one creation into the many-creations list for a spell id.

        Contract:
            - Creates the `many` list for `key` when absent.
            - Appends one disposal-tracked tuple entry to that list.
            - Rejects key collisions with non-list slots.
            - Pushes to the disposal stack only when disposal methods are declared.

        Args:
            key:
                Spell id used as the many-creation slot key.
            item:
                Resolved instance to wrap and append.
            has_disposal_methods:
                True when this spell declared disposal methods.
            disposal_methods:
                Ordered disposal method names for the creation.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the Creations manager is already cleaned.
            ValueError:
                If `key` already exists in the shared map with a non-list value.
        """
        if has_disposal_methods:
            existing_plain = self._creations.get(key)
            if existing_plain is not None:
                raise ValueError(
                    f"Key {key} already exists in creations with non-list slot."
                )
            many_list = self._disposable_creations.setdefault(key, [])
            if not isinstance(many_list, list):
                raise ValueError(
                    f"Key {key} already exists in creations with non-list slot."
                )
            disposable_entry: StoredDisposalEntry = (
                item,
                list(disposal_methods) if disposal_methods else [],
            )
            many_list.append(disposable_entry)
            self._push_disposal_creation(disposable_entry)
            return
        existing_disposable = self._disposable_creations.get(key)
        if existing_disposable is not None:
            raise ValueError(
                f"Key {key} already exists in creations with non-list slot."
            )
        many_list = self._creations.setdefault(key, [])
        if not isinstance(many_list, list):
            raise ValueError(
                f"Key {key} already exists in creations with non-list slot."
            )
        many_list.append(item)

    # ------------------------------------------------------------------
    # Extraction / restoration helpers (for transfers)
    # ------------------------------------------------------------------
    def extract_spell_creations(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Purpose:
            Remove and return all creations for one spell id from shared and spellspace scopes.

        Contract:
            - Removes at most one non-spellspace slot for the spell id.
            - Removes any spellspace entries for the spell id across all spellspace buckets.
            - Updates disposal stacks to match extracted entries.

        Args:
            spell_id:
                Spell identifier whose creations should be extracted.

        Returns:
            List[Dict[str, Any]]:
                Serialized stored-entry payloads suitable for
                `restore_spell_creations`.
        """
        
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            # Root scope entry (singleton or many list).
            value = self._creations.get(spell_id)
            if isinstance(value, list):
                many_entries = self._creations.pop(spell_id)
                for stored_value in many_entries:
                    extracted.append(
                        {
                            "scope": "many",
                            "disposable": False,
                            "stored": stored_value,
                        }
                    )
            elif value is not None and not isinstance(value, dict):
                stored_value = self._creations.pop(spell_id)
                extracted.append(
                    {
                        "scope": "unique",
                        "disposable": False,
                        "stored": stored_value,
                    }
                )
            else:
                disposable_value = self._disposable_creations.get(spell_id)
                if isinstance(disposable_value, list):
                    many_entries = self._disposable_creations.pop(spell_id)
                    for entry in many_entries:
                        self._remove_disposal_creation(entry)
                        extracted.append(
                            {
                                "scope": "many",
                                "disposable": True,
                                "stored": entry,
                            }
                        )
                elif disposable_value is not None:
                    stored_value = self._disposable_creations.pop(spell_id)
                    self._remove_disposal_creation(stored_value)
                    extracted.append(
                        {
                            "scope": "unique",
                            "disposable": True,
                            "stored": stored_value,
                        }
                    )

            # Spellspace buckets (nested dict entries in same shared store).
            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                creation = bucket.pop(spell_id)
                extracted.append(
                    {
                        "scope": "spellspace",
                        "spellspace_id": spellspace_id,
                        "disposable": False,
                        "stored": creation,
                    }
                )
                if not bucket:
                    del self._creations[spellspace_id]
            for spellspace_id, bucket in list(self._disposable_creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                entry = bucket.pop(spell_id)
                self._remove_spellspace_disposal_creation(spellspace_id, entry)
                extracted.append(
                    {
                        "scope": "spellspace",
                        "spellspace_id": spellspace_id,
                        "disposable": True,
                        "stored": entry,
                    }
                )
                if not bucket:
                    del self._disposable_creations[spellspace_id]
                    self._spellspace_disposal_stacks.pop(spellspace_id, None)
        return extracted

    def restore_spell_creations(self, spell_id: str, creations: List[Dict[str, Any]]) -> None:
        """
        Purpose:
            Restore creations previously extracted for a spell id.

        Contract:
            - Replaces any existing entries for `spell_id` across all scopes.
            - Restores non-spellspace and spellspace entries into the shared creations map.
            - Rebuilds disposal stacks for restored entries.
            - Raises when target slots do not match expected container type or scope is unknown.

        Args:
            spell_id:
                Spell identifier whose creations are being restored.
            creations:
                Entries produced by `extract_spell_creations`.

        Returns:
            None.

        Raises:
            RuntimeError:
                If a `many` entry targets a non-list slot or a spellspace entry
                targets a non-dict slot.
        """
        
        if not creations:
            return
        with self._lock:
            # Transfer restore semantics are replace-by-spell_id, not merge.
            value = self._creations.get(spell_id)
            if value is not None and not isinstance(value, dict):
                self._creations.pop(spell_id)
            disposable_value = self._disposable_creations.get(spell_id)
            if isinstance(disposable_value, list):
                many_entries = self._disposable_creations.pop(spell_id)
                for existing_creation in many_entries:
                    self._remove_disposal_creation(existing_creation)
            elif disposable_value is not None:
                self._disposable_creations.pop(spell_id)
                self._remove_disposal_creation(disposable_value)

            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                creation = bucket.pop(spell_id)
                if not bucket:
                    del self._creations[spellspace_id]
            for spellspace_id, bucket in list(self._disposable_creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                entry = bucket.pop(spell_id)
                self._remove_spellspace_disposal_creation(spellspace_id, entry)
                if not bucket:
                    del self._disposable_creations[spellspace_id]
                    self._spellspace_disposal_stacks.pop(spellspace_id, None)

            for entry in creations:
                scope = entry["scope"]
                is_disposable = entry["disposable"]
                restored_value = entry["stored"]
                if scope == "unique":
                    if is_disposable:
                        self._disposable_creations[spell_id] = restored_value
                        self._push_disposal_creation(restored_value)
                    else:
                        self._creations[spell_id] = restored_value
                elif scope == "many":
                    target_registry = (
                        self._disposable_creations
                        if is_disposable
                        else self._creations
                    )
                    if spell_id not in target_registry:
                        target_registry[spell_id] = []
                    many_list = target_registry[spell_id]
                    if not isinstance(many_list, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    many_list.append(restored_value)
                    if is_disposable:
                        self._push_disposal_creation(restored_value)
                elif scope == "spellspace":
                    spellspace_id = entry["spellspace_id"]
                    if is_disposable:
                        bucket = self._disposable_creations.setdefault(spellspace_id, {})
                        if not isinstance(bucket, dict):
                            raise RuntimeError(
                                f"Cannot restore spellspace creation for spellspace '{spellspace_id}' "
                                "into non-dict slot."
                            )
                        bucket[spell_id] = restored_value
                        self._push_spellspace_disposal_creation(
                            spellspace_id,
                            restored_value,
                        )
                    else:
                        bucket = self._creations.setdefault(spellspace_id, {})
                        if not isinstance(bucket, dict):
                            raise RuntimeError(
                                f"Cannot restore spellspace creation for spellspace '{spellspace_id}' "
                                "into non-dict slot."
                            )
                        bucket[spell_id] = restored_value
                else:
                    raise RuntimeError(
                        f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                    )

    # ------------------------------------------------------------------
    # SpellSpace helpers
    # ------------------------------------------------------------------

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Optional[Any]:
        """
        Purpose:
            Return one spellspace-scoped creation by spellspace id and spell id.

        Contract:
            - Returns None when no spellspace bucket exists for `spellspace_id`.
            - Returns None when `spell_id` is absent in the bucket.

        Args:
            spellspace_id:
                Spellspace bucket key.
            spell_id:
                Spell identifier within the spellspace bucket.

        Returns:
            Optional[Any]:
                Matching stored entry, or None when missing.
        """
        
        bucket = self._creations.get(spellspace_id)
        if not isinstance(bucket, dict):
            bucket = self._disposable_creations.get(spellspace_id)
            if not isinstance(bucket, dict):
                return None
            entry = bucket.get(spell_id)
            if entry is None:
                return None
            return entry[0]
        entry = bucket.get(spell_id)
        if entry is None:
            return None
        return entry

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

        Contract:
            - Returns the raw retained object for plain entries.
            - Returns the stored object from the disposal tuple for
              disposal-tracked entries.
            - Returns None when no retained non-spellspace entry exists.
        """
        entry = self._creations.get(spell_id)
        if entry is not None and not isinstance(entry, dict) and not isinstance(entry, list):
            return entry
        disposable_entry = self._disposable_creations.get(spell_id)
        if isinstance(disposable_entry, tuple):
            return disposable_entry[0]
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
        Purpose:
            Register one creation into a spellspace bucket.

        Contract:
            - Creates the spellspace bucket when it does not exist.
            - Rejects duplicate spell ids inside the target bucket.
            - Rejects bucket key collisions with non-dict slots.
            - Registers disposal metadata for spellspace teardown only when
              disposal methods exist.

        Args:
            spellspace_id: SpellSpace bucket identifier.
            spell_id: Spell id used as the bucket key.
            item: Object instance to register.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Returns:
            None.

        Raises:
            ValueError:
                If the spellspace slot collides with a non-dict slot or the spell id
                already exists in the spellspace bucket.
        """
        
        if has_disposal_methods:
            bucket = self._disposable_creations.setdefault(spellspace_id, {})
            if not isinstance(bucket, dict):
                raise ValueError(f"Key {spellspace_id} already exists in disposable creations with non-spellspace scope.")
            if spell_id in bucket:
                raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
            disposal_entry: StoredDisposalEntry = (
                item,
                list(disposal_methods) if disposal_methods else [],
            )
            bucket[spell_id] = disposal_entry
            self._push_spellspace_disposal_creation(spellspace_id, disposal_entry)
            return
        bucket = self._creations.setdefault(spellspace_id, {})
        if not isinstance(bucket, dict):
            raise ValueError(f"Key {spellspace_id} already exists in creations with non-spellspace scope.")
        if spell_id in bucket:
            raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
        bucket[spell_id] = item

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Purpose:
            Dispose and remove all entries for one spellspace bucket.

        Contract:
            - Drains the spellspace disposal stack before clearing non-disposable entries.
            - Removes the spellspace bucket and its disposal stack.
            - No-ops when the spellspace bucket is absent.

        Args:
            spellspace_id:
                Spellspace bucket identifier.

        Returns:
            None.

        Raises:
            ExceptionGroup:
                If one or more disposal operations fail.
        """
        
        bucket = self._creations.get(spellspace_id)
        if isinstance(bucket, dict):
            bucket.clear()
            del self._creations[spellspace_id]
        disposable_bucket = self._disposable_creations.get(spellspace_id)
        if not isinstance(disposable_bucket, dict):
            if isinstance(bucket, dict):
                self._spellspace_disposal_stacks.pop(spellspace_id, None)
            return
        errors: List[Exception] = []
        errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
        disposable_bucket.clear()
        del self._disposable_creations[spellspace_id]
        self._spellspace_disposal_stacks.pop(spellspace_id, None)
        if errors:
            raise ExceptionGroup("Errors occurred during spellspace cleanup", errors)

    def reset_for_pool(self) -> None:
        """
        Purpose:
            Clear all live creation state without destroying this manager.

        Contract:
            - Drains global and spellspace disposal stacks.
            - Clears all retained raw and disposable entries.
            - Clears shared and spellspace-scoped creation buckets.
            - Keeps the `Creations` object itself alive for later reuse.

        Returns:
            None.

        Raises:
            ExceptionGroup:
                If one or more disposal operations fail during reset.
        """
        self.check_cleaned()
        with self._lock:
            errors: List[Exception] = []
            errors.extend(self._drain_disposal_stack())
            for spellspace_id in list(self._spellspace_disposal_stacks.keys()):
                errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))

            self._creations.clear()
            self._disposable_creations.clear()
            self._spellspace_disposal_stacks.clear()
            self._disposal_stack.clear()

            if errors:
                raise ExceptionGroup("Errors occurred during pooled reset", errors)

    def reset_non_spellspace_for_pool(self) -> None:
        """
        Purpose:
            Clear only non-spellspace creation state without touching spellspace buckets.

        Contract:
            - Drains only the global disposal stack.
            - Clears only shared non-spellspace raw and disposable entries.
            - Leaves spellspace buckets and spellspace disposal stacks to the
              spellspace cleanup path.
            - Keeps the `Creations` object itself alive for later reuse.

        Returns:
            None.

        Raises:
            ExceptionGroup:
                If one or more non-spellspace disposal operations fail during reset.
        """
        self.check_cleaned()
        with self._lock:
            errors: List[Exception] = []
            errors.extend(self._drain_disposal_stack())

            for key, item in list(self._creations.items()):
                if not isinstance(item, dict):
                    del self._creations[key]
            for key, item in list(self._disposable_creations.items()):
                if not isinstance(item, dict):
                    del self._disposable_creations[key]

            self._disposal_stack.clear()

            if errors:
                raise ExceptionGroup(
                    "Errors occurred during pooled non-spellspace reset",
                    errors,
                )
