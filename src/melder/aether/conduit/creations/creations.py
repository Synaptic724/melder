from collections import deque
from threading import RLock
from typing import List, Optional, Dict, Any

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import IConduit, ICreations
from melder.aether.conduit.creations.creation import Creation
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

# TODO: Narrow this manager's public surface so storage/disposal internals are
# not the default interface exposed to the rest of the conduit runtime.

class Creations(Cleanable, ICreations):
    """
    Conduit-owned registry for live creation objects and their disposal state.

    `Creations` is the runtime store behind meld reuse. It tracks live objects
    under the spell's lifecycle contract, records disposal metadata, and owns
    the ordered cleanup stacks that are drained when the conduit tears down.

    Responsibilities:
    - store non-spellspace and spellspace-scoped creations in one shared map
    - preserve lifecycle semantics for singleton, many, and spellspace routes
    - record disposal ordering through global and spellspace-local stacks
    - support extraction/restoration workflows used by ownership transfer

    Contract:
    - cleanup is idempotent and drains disposal stacks before references are
      nulled
    - disposal method order comes from `Creation.disposal_method_names`
    - cleanup errors are aggregated and raised only after teardown work
      finishes
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, conduit: IConduit):
        """
        Purpose:
            Initialize the conduit creations registry.

        Contract:
            - Owns one shared creations map for non-spellspace and spellspace entries.
            - Owns one global disposal stack and per-spellspace disposal stacks.

        Args:
            conduit:
                Conduit that owns this Creations manager.

        Returns:
            None.

        Raises:
            RuntimeError:
                If conduit state is missing.
        """
        super().__init__()
        self._conduit: IConduit = conduit
        self._id: str = conduit._id

        if conduit._conduit_state is None:
            raise RuntimeError("Conduit state is not initialized.")
        self._conduit_state = conduit._conduit_state

        self._lock = RLock()
        self._disposal_stack: deque = deque()
        self._spellspace_disposal_stacks: Dict[str, deque] = {}

        # Single shared storage for all lifecycle scopes and spellspace buckets.
        # Non-spellspace entries are keyed by spell_id.
        # Spellspace entries are keyed by spellspace_id and hold nested buckets.
        self._creations: Dict[str, Any] = {}


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
            self._spellspace_disposal_stacks.clear()
            self._disposal_stack.clear()

            self._creations = None
            self._spellspace_disposal_stacks = None
            self._conduit = None
            self._disposal_stack = None

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
            errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
            for item in bucket.values():
                if not item.has_disposal_methods:
                    item.cleanup()
            bucket.clear()
            del self._creations[spellspace_id]
        self._spellspace_disposal_stacks.clear()
        return errors

    def _attempt_cleanup(self, creation: Creation) -> Optional[Exception]:
        """
        Attempt disposal for one creation using its configured method order.

        This helper is the core disposal-policy interpreter. It does not guess
        or probe multiple protocols beyond the configured method-name list on
        the `Creation`. The first configured method that exists is called; if it
        raises, the error is wrapped and returned for later aggregation.

        Args:
            creation: Creation wrapper whose value may expose one of the
                configured disposal methods.

        Returns:
            Optional[Exception]: Wrapped disposal error when the chosen cleanup
            method fails, otherwise `None`.
        """
        item = creation.value
        if item is None:
            return None
        method_names = creation.disposal_method_names or []
        if not method_names:
            return None

        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
                return None
            except Exception as ex:
                return RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")

        return None

    def _push_disposal_creation(self, creation: Creation) -> None:
        """
        Register one creation on the global disposal stack.

        Only creations that actually declare disposal methods are pushed, so the
        stack represents "must attempt explicit disposal" work rather than every
        live object in the registry.
        """
        if creation.has_disposal_methods:
            self._disposal_stack.appendleft(creation)

    def _push_spellspace_disposal_creation(self, spellspace_id: str, creation: Creation) -> None:
        """
        Register one creation on its spellspace-local disposal stack.

        Spellspace-scoped creations use a separate stack so teardown can drain
        each spellspace bucket deterministically without mixing it into the
        global conduit-level disposal order.
        """
        if creation.has_disposal_methods:
            stack = self._spellspace_disposal_stacks.setdefault(spellspace_id, deque())
            stack.appendleft(creation)

    def _remove_disposal_creation(self, creation: Creation) -> None:
        """
        Remove one creation from the global disposal stack if present.

        This is primarily used by extraction/transfer flows that move creations
        out of the registry and need the disposal bookkeeping to stay aligned
        with the moved objects.
        """
        if not creation.has_disposal_methods:
            return
        if not self._disposal_stack:
            return
        self._disposal_stack = deque(
            item for item in self._disposal_stack
            if item is not creation
        )

    def _remove_spellspace_disposal_creation(self, spellspace_id: str, creation: Creation) -> None:
        """
        Remove one creation from a spellspace-local disposal stack if present.

        This is the spellspace-scoped counterpart to `_remove_disposal_creation`
        and keeps per-spellspace disposal bookkeeping aligned with extraction or
        bucket-clearing flows.
        """
        if not creation.has_disposal_methods:
            return
        stack = self._spellspace_disposal_stacks.get(spellspace_id)
        if not stack:
            return
        self._spellspace_disposal_stacks[spellspace_id] = deque(
            item for item in stack
            if item is not creation
        )

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
            creation = self._disposal_stack.popleft()
            maybe_error = self._attempt_cleanup(creation)
            if maybe_error:
                errors.append(maybe_error)
            creation.cleanup()
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
            creation = stack.popleft()
            maybe_error = self._attempt_cleanup(creation)
            if maybe_error:
                errors.append(maybe_error)
            creation.cleanup()
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
            - Inserts one `Creation` under `key` in the shared creations map.
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
        self.check_cleaned()
        if key in self._creations:
            raise ValueError(f"Key {key} already exists in creations.")
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        self._creations[key] = creation
        if has_disposal_methods:
            self._push_disposal_creation(creation)

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
            - Appends one `Creation` entry to that list.
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
        self.check_cleaned()
        many_list = self._creations.setdefault(key, [])
        if not isinstance(many_list, list):
            raise ValueError(
                f"Key {key} already exists in creations with non-list slot."
            )
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        many_list.append(creation)
        self._push_disposal_creation(creation)

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
                Serialized creation entries suitable for `restore_spell_creations`.
        """
        self.check_cleaned()
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            # Root scope entry (singleton or many list).
            value = self._creations.get(spell_id)
            if isinstance(value, Creation):
                creation = self._creations.pop(spell_id)
                self._remove_disposal_creation(creation)
                extracted.append({"scope": "unique", "creation": creation})
            elif isinstance(value, list):
                many_entries = self._creations.pop(spell_id)
                for creation in many_entries:
                    self._remove_disposal_creation(creation)
                    extracted.append({"scope": "many", "creation": creation})

            # Spellspace buckets (nested dict entries in same shared store).
            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                creation = bucket.pop(spell_id)
                self._remove_spellspace_disposal_creation(spellspace_id, creation)
                extracted.append(
                    {
                        "scope": "spellspace",
                        "spellspace_id": spellspace_id,
                        "creation": creation,
                    }
                )
                if not bucket:
                    del self._creations[spellspace_id]
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
        self.check_cleaned()
        if not creations:
            return
        with self._lock:
            # Transfer restore semantics are replace-by-spell_id, not merge.
            value = self._creations.get(spell_id)
            if isinstance(value, Creation):
                existing_creation = self._creations.pop(spell_id)
                self._remove_disposal_creation(existing_creation)
            elif isinstance(value, list):
                many_entries = self._creations.pop(spell_id)
                for existing_creation in many_entries:
                    self._remove_disposal_creation(existing_creation)

            for spellspace_id, bucket in list(self._creations.items()):
                if not isinstance(bucket, dict):
                    continue
                if spell_id not in bucket:
                    continue
                creation = bucket.pop(spell_id)
                self._remove_spellspace_disposal_creation(spellspace_id, creation)
                if not bucket:
                    del self._creations[spellspace_id]
                    self._spellspace_disposal_stacks.pop(spellspace_id, None)

            for entry in creations:
                scope = entry["scope"]
                restored_creation: Creation = entry["creation"]
                if scope == "unique":
                    self._creations[spell_id] = restored_creation
                    self._push_disposal_creation(restored_creation)
                elif scope == "many":
                    if spell_id not in self._creations:
                        self._creations[spell_id] = []
                    many_list = self._creations[spell_id]
                    if not isinstance(many_list, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    many_list.append(restored_creation)
                    self._push_disposal_creation(restored_creation)
                elif scope == "spellspace":
                    spellspace_id = entry["spellspace_id"]
                    bucket = self._creations.setdefault(spellspace_id, {})
                    if not isinstance(bucket, dict):
                        raise RuntimeError(
                            f"Cannot restore spellspace creation for spellspace '{spellspace_id}' "
                            "into non-dict slot."
                        )
                    bucket[spell_id] = restored_creation
                    self._push_spellspace_disposal_creation(
                        spellspace_id,
                        restored_creation,
                    )
                else:
                    raise RuntimeError(
                        f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                    )

    # ------------------------------------------------------------------
    # SpellSpace helpers
    # ------------------------------------------------------------------

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Optional[Creation]:
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
            Optional[Creation]:
                Matching creation wrapper, or None when missing.
        """
        self.check_cleaned()
        bucket = self._creations.get(spellspace_id)
        if not isinstance(bucket, dict):
            return None
        return bucket.get(spell_id)

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
            - Registers disposal metadata for spellspace teardown.

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
        self.check_cleaned()
        bucket = self._creations.setdefault(spellspace_id, {})
        if not isinstance(bucket, dict):
            raise ValueError(f"Key {spellspace_id} already exists in creations with non-spellspace scope.")
        if spell_id in bucket:
            raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        bucket[spell_id] = creation
        self._push_spellspace_disposal_creation(spellspace_id, creation)

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
        self.check_cleaned()
        bucket = self._creations.get(spellspace_id)
        if not isinstance(bucket, dict):
            return
        errors: List[Exception] = []
        errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
        for item in bucket.values():
            if not item.has_disposal_methods:
                item.cleanup()
        bucket.clear()
        del self._creations[spellspace_id]
        self._spellspace_disposal_stacks.pop(spellspace_id, None)
        if errors:
            raise ExceptionGroup("Errors occurred during spellspace cleanup", errors)
