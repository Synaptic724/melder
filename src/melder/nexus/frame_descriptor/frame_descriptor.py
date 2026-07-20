import threading
from typing import TYPE_CHECKING, Dict, Optional, Set, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.aether.aetheric_frame.aetheric_frame_configuration import (
        AethericFrameConfiguration,
    )
    from melder.nexus.frame_descriptor.conduit_record import ConduitRecord
    from melder.nexus.frame_descriptor.frame_record import FrameRecord
    from melder.nexus.frame_descriptor.spell_record import SpellRecord


class FrameDescriptor(Cleanable):
    """

    Purpose:
        Aggregate the Nexus-owned metadata and indexes for one frame-scoped
        state surface.

    Contract:
        - There is at most one descriptor per frame name.
        - The descriptor may reference the live runtime frame and bound frame
          posture, but it does not own their runtime lifecycle.
        - The descriptor owns Nexus-side records and indexes derived from the
          frame: `FrameRecord`, `ConduitRecord`, `SpellRecord`, and the
          related secondary indexes.
        - Cleanup is idempotent and clears owned metadata while dropping any
          non-owned references.

    Threading:
        Uses one instance `threading.RLock` to serialize multi-step updates to
        record ownership and secondary-index maintenance.

    Lifecycle:
        Cleanup cascades into all owned record objects before dropping indexes
        and references.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameDescriptor runtime object. Melder kernel machinery: read it to "
        "understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_frame_handle",
        "_frame_configuration",
        "_frame_overview",
        "_conduit_records_by_id",
        "_spell_records_by_key",
        "_spell_keys_by_conduit_id",
        "_spell_keys_by_spellbook_id",
    ]

    def __init__(self, frame_name: str) -> None:
        """
        Initialize one empty Nexus-side frame descriptor.

        Purpose:
            Construct the per-frame Nexus aggregate that will later host frame,
            conduit, and spell metadata records.

        Contract:
            - `frame_name` must remain the stable identity of the descriptor for
              its entire lifetime.
            - Runtime frame/configuration references start unset.
            - All record/index stores start empty.

        Args:
            frame_name:
                Stable frame name represented by this descriptor.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._frame_handle: Optional[AethericFrame] = None
        self._frame_configuration: Optional[AethericFrameConfiguration] = None
        self._frame_overview: Optional[FrameRecord] = None
        self._conduit_records_by_id: Dict[str, ConduitRecord] = {}
        self._spell_records_by_key: Dict[Tuple[str, str], SpellRecord] = {}
        self._spell_keys_by_conduit_id: Dict[str, Set[Tuple[str, str]]] = {}
        self._spell_keys_by_spellbook_id: Dict[str, Set[Tuple[str, str]]] = {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup the descriptor.

        Purpose:
            Tear down all descriptor-owned records, indexes, and references in
            one deterministic pass.

        Contract:
            - Safe to call more than once.
            - Cleans owned records before clearing indexes.
            - Drops non-owned runtime references after record cleanup.

        Threading:
            Acquires the descriptor lock so no other record/index mutation can
            interleave with teardown.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._frame_overview is not None:
                self._frame_overview.cleanup()
            for conduit_record in self._conduit_records_by_id.values():
                conduit_record.cleanup()
            for spell_record in self._spell_records_by_key.values():
                spell_record.cleanup()
            self._conduit_records_by_id.clear()
            self._spell_records_by_key.clear()
            self._spell_keys_by_conduit_id.clear()
            self._spell_keys_by_spellbook_id.clear()
            del self._frame_handle
            del self._frame_configuration
            del self._frame_overview
            del self._conduit_records_by_id
            del self._spell_records_by_key
            del self._spell_keys_by_conduit_id
            del self._spell_keys_by_spellbook_id
            del self._frame_name
        del self._lock


    @property
    def frame_name(self) -> str:
        """
        Return the stable descriptor frame name.

        Purpose:
            Expose the frame identity that anchors every record and index in
            this descriptor.

        Returns:
            str: Frame name for this descriptor.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def frame_handle(self) -> Optional[AethericFrame]:
        """
        Return the current runtime frame reference when known.

        Purpose:
            Expose the live runtime frame reference cached on the descriptor
            when available.

        Returns:
            Optional[AethericFrame]: Current runtime frame handle.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_handle

    @property
    def frame_configuration(self) -> Optional[AethericFrameConfiguration]:
        """
        Return the currently attached frame posture/configuration reference.

        Purpose:
            Expose the bound frame posture cached on the descriptor.

        Returns:
            Optional[AethericFrameConfiguration]: Bound frame configuration
            reference when known.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_configuration

    @property
    def frame_overview(self) -> Optional["FrameRecord"]:
        """
        Return the owned frame overview record when published.

        Purpose:
            Expose the descriptor-owned frame summary record when one has been
            published.

        Returns:
            Optional[FrameRecord]: Current frame overview record.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_overview

    @property
    def conduit_records_by_id(self) -> Dict[str, "ConduitRecord"]:
        """
        Return a snapshot of the descriptor-owned conduit record map.

        Purpose:
            Expose the current conduit-record mapping without handing callers
            the live mutable dictionary.

        Returns:
            Dict[str, ConduitRecord]: Snapshot of conduit records by conduit
            id.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._conduit_records_by_id)

    @property
    def spell_records_by_key(self) -> Dict[Tuple[str, str], SpellRecord]:
        """
        Return a snapshot of the descriptor-owned spell record map.

        Purpose:
            Expose the current spell-record mapping without handing callers the
            live mutable dictionary.

        Returns:
            Dict[Tuple[str, str], SpellRecord]: Snapshot of spell records by
            `(spellbook_id, spell_id)`.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._spell_records_by_key)

    @property
    def spell_keys_by_conduit_id(self) -> Dict[str, Set[Tuple[str, str]]]:
        """
        Return a snapshot of the descriptor-owned conduit -> spell-key index.

        Purpose:
            Expose the secondary index from conduit id to owned spell keys.

        Returns:
            Dict[str, Set[Tuple[str, str]]]: Snapshot of spell keys grouped by
            conduit id.
        """
        self.check_cleaned()
        with self._lock:
            return {
                conduit_id: set(spell_keys)
                for conduit_id, spell_keys in self._spell_keys_by_conduit_id.items()
            }

    @property
    def spell_keys_by_spellbook_id(self) -> Dict[str, Set[Tuple[str, str]]]:
        """
        Return a snapshot of the descriptor-owned spellbook -> spell-key index.

        Purpose:
            Expose the secondary index from spellbook id to owned spell keys.

        Returns:
            Dict[str, Set[Tuple[str, str]]]: Snapshot of spell keys grouped by
            spellbook id.
        """
        self.check_cleaned()
        with self._lock:
            return {
                spellbook_id: set(spell_keys)
                for spellbook_id, spell_keys in self._spell_keys_by_spellbook_id.items()
            }

    def set_frame_handle(self, frame_handle: Optional[AethericFrame]) -> None:
        """
        Attach or replace the runtime frame reference.

        Purpose:
            Cache or clear the descriptor's live runtime frame reference.

        Contract:
            This method stores a reference only; it does not transfer frame
            ownership into the descriptor.

        Args:
            frame_handle:
                Live runtime frame handle or None when clearing the cached
                reference.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_handle = frame_handle

    def set_frame_configuration(
            self,
            frame_configuration: Optional[AethericFrameConfiguration],
    ) -> None:
        """
        Attach or replace the bound frame configuration reference.

        Purpose:
            Cache or clear the frame posture reference associated with this
            descriptor.

        Contract:
            This method stores a reference only; it does not own or finalize the
            supplied configuration.

        Args:
            frame_configuration:
                Bound frame configuration reference or None when clearing the
                cached posture.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_configuration = frame_configuration

    def set_frame_overview(self, frame_overview: FrameRecord) -> None:
        """
        Replace the owned frame overview record.

        Purpose:
            Install a new descriptor-owned frame summary record.

        Contract:
            When a different overview record is already owned, the older record
            is cleaned before replacement.

        Args:
            frame_overview:
                New frame overview record to own.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._frame_overview
            if existing is not None and existing is not frame_overview:
                existing.cleanup()
            self._frame_overview = frame_overview

    def clear_runtime_publication_state(self) -> None:
        """
        Clear all runtime-derived publication state while keeping the descriptor.

        Purpose:
            Drop the live frame reference, bound frame posture, frame overview,
            conduit records, spell records, and secondary indexes after the
            backing `AethericFrame` is detached.

        Contract:
            - Keeps the descriptor object and stable `frame_name` alive.
            - Cleans every owned record object before clearing the primary and
              secondary stores.
            - Leaves the descriptor ready for later repopulation if the same
              frame name is published again.

        Threading:
            Runs under the descriptor lock so detach cleanup cannot interleave
            with publication or index mutation.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_handle = None
            self._frame_configuration = None
            if self._frame_overview is not None:
                self._frame_overview.cleanup()
                self._frame_overview = None
            for conduit_record in self._conduit_records_by_id.values():
                conduit_record.cleanup()
            for spell_record in self._spell_records_by_key.values():
                spell_record.cleanup()
            self._conduit_records_by_id.clear()
            self._spell_records_by_key.clear()
            self._spell_keys_by_conduit_id.clear()
            self._spell_keys_by_spellbook_id.clear()

    def upsert_conduit_record(self, conduit_record: ConduitRecord) -> None:
        """
        Upsert one conduit record owned by this descriptor.

        Purpose:
            Store or replace one conduit record in the descriptor-owned primary
            conduit registry.

        Contract:
            - Replacing an existing different record cleans the older record
              before storing the new one.
            - Re-storing the same record object is a no-op for lifecycle
              purposes.
            - The descriptor takes ownership of the stored record.

        Args:
            conduit_record:
                Conduit record to store and own.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._conduit_records_by_id.get(conduit_record.conduit_id)
            if existing is not None and existing is not conduit_record:
                existing.cleanup()
            self._conduit_records_by_id[conduit_record.conduit_id] = conduit_record

    def remove_conduit_record(self, conduit_id: str) -> None:
        """
        Remove one conduit record owned by this descriptor.

        Purpose:
            Remove a conduit record from the primary registry and clean it if it
            exists.

        Args:
            conduit_id:
                Conduit id whose record should be removed.
        Contract:
            - Missing conduit ids are treated as a no-op.
            - Existing records are removed from the primary registry before
              being cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._conduit_records_by_id.pop(conduit_id, None)
            if existing is not None:
                existing.cleanup()

    def upsert_spell_record(self, spell_record: SpellRecord) -> None:
        """
        Upsert one spell record and refresh descriptor-local indexes.

        Purpose:
            Store or replace a spell record and keep the descriptor's secondary
            indexes consistent with the new state.

        Contract:
            - Existing different records are removed from indexes and cleaned
              before replacement.
            - The spellbook and conduit indexes are rebuilt from the new record
              state.

        Args:
            spell_record:
                Spell record to store and own.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            record_key = spell_record.record_key
            existing = self._spell_records_by_key.get(record_key)
            if existing is not None:
                self._discard_spell_from_indexes(existing)
                if existing is not spell_record:
                    existing.cleanup()
            self._spell_records_by_key[record_key] = spell_record
            self._ensure_spellbook_spell_index(spell_record.origin_spellbook_id).add(
                record_key
            )
            if spell_record.owner_conduit_id:
                self._ensure_conduit_spell_index(spell_record.owner_conduit_id).add(
                    record_key
                )

    def remove_spell_record(self, record_key: Tuple[str, str]) -> None:
        """
        Remove one spell record and clear its descriptor-local indexes.

        Purpose:
            Remove a spell record from the primary registry and tear down its
            secondary-index membership.

        Args:
            record_key:
                Canonical `(spellbook_id, spell_id)` key for the record to
                remove.
        Contract:
            - Missing keys are treated as a no-op.
            - Existing records are removed from the primary registry before
              their secondary-index memberships are discarded.
            - Owned records are cleaned after index teardown.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._spell_records_by_key.pop(record_key, None)
            if existing is None:
                return
            self._discard_spell_from_indexes(existing)
            existing.cleanup()

    def _ensure_conduit_spell_index(
            self,
            conduit_id: str,
    ) -> Set[Tuple[str, str]]:
        """
        Return the conduit -> spell-key index set, creating it when missing.

        Purpose:
            Provide mutable storage for the conduit-to-spell secondary index.

        Args:
            conduit_id:
                Conduit id.

        Contract:
            - Returns the live mutable set owned by the descriptor.
            - Creates the secondary-index bucket on demand when the conduit has
              not been seen yet.

        Returns:
            Set[Tuple[str, str]]: Mutable spell-key set.
        """
        spell_keys = self._spell_keys_by_conduit_id.get(conduit_id)
        if spell_keys is None:
            spell_keys = set()
            self._spell_keys_by_conduit_id[conduit_id] = spell_keys
        return spell_keys

    def _ensure_spellbook_spell_index(
            self,
            spellbook_id: str,
    ) -> Set[Tuple[str, str]]:
        """
        Return the spellbook -> spell-key index set, creating it when missing.

        Purpose:
            Provide mutable storage for the spellbook-to-spell secondary index.

        Args:
            spellbook_id:
                Spellbook id.

        Contract:
            - Returns the live mutable set owned by the descriptor.
            - Creates the secondary-index bucket on demand when the spellbook
              has not been seen yet.

        Returns:
            Set[Tuple[str, str]]: Mutable spell-key set.
        """
        spell_keys = self._spell_keys_by_spellbook_id.get(spellbook_id)
        if spell_keys is None:
            spell_keys = set()
            self._spell_keys_by_spellbook_id[spellbook_id] = spell_keys
        return spell_keys

    def _discard_spell_from_indexes(self, spell_record: SpellRecord) -> None:
        """
        Remove one spell record's key from descriptor-local indexes.

        Purpose:
            Keep secondary indexes synchronized when a spell record is removed
            or replaced.

        Args:
            spell_record:
                Spell record whose index memberships should be removed.
        Contract:
            - Removes the spell key from both spellbook-level and conduit-level
              secondary indexes when present.
            - Deletes empty secondary-index buckets after the key is removed so
              the descriptor does not retain dead index shells.
            - Does not clean the spell record; caller-owned removal paths decide
              record lifecycle separately.
        """
        record_key = spell_record.record_key
        spellbook_spell_keys = self._spell_keys_by_spellbook_id.get(
            spell_record.origin_spellbook_id
        )
        if spellbook_spell_keys is not None:
            spellbook_spell_keys.discard(record_key)
            if len(spellbook_spell_keys) == 0:
                self._spell_keys_by_spellbook_id.pop(
                    spell_record.origin_spellbook_id,
                    None,
                )

        if spell_record.owner_conduit_id:
            conduit_spell_keys = self._spell_keys_by_conduit_id.get(
                spell_record.owner_conduit_id
            )
            if conduit_spell_keys is not None:
                conduit_spell_keys.discard(record_key)
                if len(conduit_spell_keys) == 0:
                    self._spell_keys_by_conduit_id.pop(
                        spell_record.owner_conduit_id,
                        None,
                    )


