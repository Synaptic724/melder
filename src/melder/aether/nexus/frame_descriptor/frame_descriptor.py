import threading
from typing import Dict, Optional, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IAethericFrame


class FrameDescriptor(Cleanable):
    """
    Internal

    Nexus-owned aggregate for one frame-scoped state surface.

    Purpose:
        Collect the frame-scoped state Nexus needs to reason about one frame in
        one place instead of scattering that state across multiple flat Nexus
        fields.

    Contract:
        - One descriptor per frame name.
        - May hold references to the live runtime frame and bound frame
          configuration, but does not own their lifecycle.
        - Owns Nexus-side metadata objects such as `FrameRecord` and
          `NexusFrameRecord`.
        - Cleanup is idempotent and clears owned metadata while dropping any
          non-owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_frame_handle",
        "_frame_configuration",
        "_frame_overview",
        "_nexus_frame_record",
        "_conduit_records_by_id",
        "_spell_records_by_key",
        "_spell_keys_by_conduit_id",
        "_spell_keys_by_spellbook_id",
    ]

    def __init__(self, frame_name: str) -> None:
        """
        Initialize one empty Nexus-side frame descriptor.

        Args:
            frame_name:
                Stable frame name represented by this descriptor.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._frame_handle: Optional[IAethericFrame] = None
        self._frame_configuration: Optional[AethericFrameConfiguration] = None
        self._frame_overview: Optional[FrameRecord] = None
        self._nexus_frame_record: Optional[NexusFrameRecord] = None
        self._conduit_records_by_id: Dict[str, ConduitRecord] = {}
        self._spell_records_by_key: Dict[Tuple[str, str], SpellRecord] = {}
        self._spell_keys_by_conduit_id: Dict[str, Set[Tuple[str, str]]] = {}
        self._spell_keys_by_spellbook_id: Dict[str, Set[Tuple[str, str]]] = {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup the descriptor.

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
            if self._nexus_frame_record is not None:
                self._nexus_frame_record.cleanup()
            for conduit_record in self._conduit_records_by_id.values():
                conduit_record.cleanup()
            for spell_record in self._spell_records_by_key.values():
                spell_record.cleanup()
            self._conduit_records_by_id.clear()
            self._spell_records_by_key.clear()
            self._spell_keys_by_conduit_id.clear()
            self._spell_keys_by_spellbook_id.clear()
            self._frame_handle = None
            self._frame_configuration = None
            self._frame_overview = None
            self._nexus_frame_record = None
            self._conduit_records_by_id = None
            self._spell_records_by_key = None
            self._spell_keys_by_conduit_id = None
            self._spell_keys_by_spellbook_id = None
            self._frame_name = None
        self._lock = None


    @property
    def frame_name(self) -> str:
        """
        Return the stable descriptor frame name.

        Returns:
            str: Frame name for this descriptor.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def frame_handle(self) -> Optional[IAethericFrame]:
        """
        Return the current runtime frame reference when known.

        Returns:
            Optional[IAethericFrame]: Current runtime frame handle.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_handle

    @property
    def frame_configuration(self) -> Optional[AethericFrameConfiguration]:
        """
        Return the currently attached frame posture/configuration reference.

        Returns:
            Optional[AethericFrameConfiguration]: Bound frame configuration
            reference when known.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_configuration

    @property
    def frame_overview(self) -> Optional[FrameRecord]:
        """
        Return the owned frame overview record when published.

        Returns:
            Optional[FrameRecord]: Current frame overview record.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_overview

    @property
    def nexus_frame_record(self) -> Optional[NexusFrameRecord]:
        """
        Return the owned Nexus-managed frame metadata record when present.

        Returns:
            Optional[NexusFrameRecord]: Current Nexus-managed frame record.
        """
        self.check_cleaned()
        with self._lock:
            return self._nexus_frame_record

    @property
    def conduit_records_by_id(self) -> Dict[str, ConduitRecord]:
        """
        Return a snapshot of the descriptor-owned conduit record map.

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

    def set_frame_handle(self, frame_handle: Optional[IAethericFrame]) -> None:
        """
        Attach or replace the runtime frame reference.

        Args:
            frame_handle:
                Live runtime frame handle or None.
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

        Args:
            frame_configuration:
                Bound frame configuration reference or None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_configuration = frame_configuration

    def set_frame_overview(self, frame_overview: FrameRecord) -> None:
        """
        Replace the owned frame overview record.

        Args:
            frame_overview:
                New frame overview record.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._frame_overview
            if existing is not None and existing is not frame_overview:
                existing.cleanup()
            self._frame_overview = frame_overview

    def set_nexus_frame_record(
            self,
            nexus_frame_record: Optional[NexusFrameRecord],
    ) -> None:
        """
        Replace the owned Nexus-managed frame metadata record.

        Args:
            nexus_frame_record:
                New Nexus-managed frame record or None.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._nexus_frame_record
            if existing is not None and existing is not nexus_frame_record:
                existing.cleanup()
            self._nexus_frame_record = nexus_frame_record

    def upsert_conduit_record(self, conduit_record: ConduitRecord) -> None:
        """
        Upsert one conduit record owned by this descriptor.

        Args:
            conduit_record:
                Conduit record to store.
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

        Args:
            conduit_id:
                Conduit id to remove.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._conduit_records_by_id.pop(conduit_id, None)
            if existing is not None:
                existing.cleanup()

    def upsert_spell_record(self, spell_record: SpellRecord) -> None:
        """
        Upsert one spell record and refresh descriptor-local indexes.

        Args:
            spell_record:
                Spell record to store.
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

        Args:
            record_key:
                Canonical `(spellbook_id, spell_id)` key.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._spell_records_by_key.pop(record_key, None)
            if existing is None:
                return
            self._discard_spell_from_indexes(existing)
            existing.cleanup()

    def detach_nexus_frame_record(self) -> Optional[NexusFrameRecord]:
        """
        Detach and return the owned Nexus-managed frame metadata record.

        Returns:
            Optional[NexusFrameRecord]: Detached record when present.
        """
        self.check_cleaned()
        with self._lock:
            nexus_frame_record = self._nexus_frame_record
            self._nexus_frame_record = None
            return nexus_frame_record

    def _ensure_conduit_spell_index(
            self,
            conduit_id: str,
    ) -> Set[Tuple[str, str]]:
        """
        Return the conduit -> spell-key index set, creating it when missing.

        Args:
            conduit_id:
                Conduit id.

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

        Args:
            spellbook_id:
                Spellbook id.

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

        Args:
            spell_record:
                Spell record whose indexes should be removed.
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
