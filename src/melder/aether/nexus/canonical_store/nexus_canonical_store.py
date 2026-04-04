from typing import Dict, Optional, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.nexus.canonical_store.frame_record import FrameRecord
from melder.aether.nexus.canonical_store.conduit_record import ConduitRecord
from melder.aether.nexus.canonical_store.spell_record import SpellRecord


class NexusCanonicalStore(Cleanable):
    """
    Internal

    Nexus-owned primary store plus secondary indexes for passive canonical
    frame/conduit/spell records.

    Purpose:
        Keep the first passive-ingest slice fast and simple with hash-map
        primary storage and set-backed secondary indexes.

    Contract:
        - Primary records are owned here.
        - Secondary indexes are maintained here, never by producers.
        - Methods are deterministic and idempotent for repeated upserts of the
          same keys.
        - Cleanup is idempotent and clears all owned records and indexes.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "frame_records_by_name",
        "conduit_records_by_id",
        "spell_records_by_key",
        "conduit_ids_by_frame_name",
        "spell_keys_by_frame_name",
        "spell_keys_by_conduit_id",
        "spell_keys_by_spellbook_id",
    ]

    def __init__(self) -> None:
        """
        Initialize the empty canonical Nexus store.

        Returns:
            None.
        """
        super().__init__()
        self.frame_records_by_name: Dict[str, FrameRecord] = {}
        self.conduit_records_by_id: Dict[str, ConduitRecord] = {}
        self.spell_records_by_key: Dict[Tuple[str, str], SpellRecord] = {}
        self.conduit_ids_by_frame_name: Dict[str, Set[str]] = {}
        self.spell_keys_by_frame_name: Dict[str, Set[Tuple[str, str]]] = {}
        self.spell_keys_by_conduit_id: Dict[str, Set[Tuple[str, str]]] = {}
        self.spell_keys_by_spellbook_id: Dict[str, Set[Tuple[str, str]]] = {}

    def upsert_frame_record(self, record: FrameRecord) -> None:
        """
        Upsert one frame record by frame name.

        Args:
            record:
                Frame record to store.

        Returns:
            None.
        """
        self.check_cleaned()
        existing = self.frame_records_by_name.get(record.frame_name)
        if existing is not None and existing is not record:
            existing.cleanup()
        self.frame_records_by_name[record.frame_name] = record

    def upsert_conduit_record(self, record: ConduitRecord) -> None:
        """
        Upsert one conduit record and refresh frame grouping indexes.

        Args:
            record:
                Conduit record to store.

        Returns:
            None.
        """
        self.check_cleaned()
        existing = self.conduit_records_by_id.get(record.conduit_id)
        if existing is not None:
            if existing.frame_name != record.frame_name:
                self._discard_conduit_from_frame_index(
                    existing.frame_name,
                    record.conduit_id,
                )
            if existing is not record:
                existing.cleanup()

        self.conduit_records_by_id[record.conduit_id] = record
        self._ensure_frame_conduit_index(record.frame_name).add(record.conduit_id)

    def remove_conduit_record(self, conduit_id: str) -> None:
        """
        Remove one conduit record and its frame grouping membership.

        Args:
            conduit_id:
                Conduit id to remove.

        Returns:
            None.
        """
        self.check_cleaned()
        existing = self.conduit_records_by_id.pop(conduit_id, None)
        if existing is None:
            return
        self._discard_conduit_from_frame_index(existing.frame_name, conduit_id)
        existing.cleanup()

    def upsert_spell_record(self, record: SpellRecord) -> None:
        """
        Upsert one spell record and refresh spell grouping indexes.

        Args:
            record:
                Spell record to store.

        Returns:
            None.
        """
        self.check_cleaned()
        record_key = record.record_key
        existing = self.spell_records_by_key.get(record_key)
        if existing is not None:
            self._discard_spell_from_indexes(existing)
            if existing is not record:
                existing.cleanup()

        self.spell_records_by_key[record_key] = record
        self._ensure_frame_spell_index(record.frame_name).add(record_key)
        self._ensure_spellbook_spell_index(record.origin_spellbook_id).add(record_key)
        if record.owner_conduit_id:
            self._ensure_conduit_spell_index(record.owner_conduit_id).add(record_key)

    def remove_spell_record(self, record_key: Tuple[str, str]) -> None:
        """
        Remove one spell record and all of its secondary index entries.

        Args:
            record_key:
                Canonical `(origin_spellbook_id, spell_id)` key.

        Returns:
            None.
        """
        self.check_cleaned()
        existing = self.spell_records_by_key.pop(record_key, None)
        if existing is None:
            return
        self._discard_spell_from_indexes(existing)
        existing.cleanup()

    def cleanup(self) -> None:
        """
        Idempotently clear all canonical records and indexes.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True

        for record in list(self.frame_records_by_name.values()):
            record.cleanup()
        for record in list(self.conduit_records_by_id.values()):
            record.cleanup()
        for record in list(self.spell_records_by_key.values()):
            record.cleanup()

        self.frame_records_by_name.clear()
        self.conduit_records_by_id.clear()
        self.spell_records_by_key.clear()
        self.conduit_ids_by_frame_name.clear()
        self.spell_keys_by_frame_name.clear()
        self.spell_keys_by_conduit_id.clear()
        self.spell_keys_by_spellbook_id.clear()

        self.frame_records_by_name = None
        self.conduit_records_by_id = None
        self.spell_records_by_key = None
        self.conduit_ids_by_frame_name = None
        self.spell_keys_by_frame_name = None
        self.spell_keys_by_conduit_id = None
        self.spell_keys_by_spellbook_id = None

    def _ensure_frame_conduit_index(self, frame_name: str) -> Set[str]:
        """
        Return the frame -> conduit-id index set, creating it when missing.

        Args:
            frame_name:
                Frame name.

        Returns:
            Set[str]: Mutable conduit-id set.
        """
        conduit_ids = self.conduit_ids_by_frame_name.get(frame_name)
        if conduit_ids is None:
            conduit_ids = set()
            self.conduit_ids_by_frame_name[frame_name] = conduit_ids
        return conduit_ids

    def _ensure_frame_spell_index(
            self,
            frame_name: str,
    ) -> Set[Tuple[str, str]]:
        """
        Return the frame -> spell-key index set, creating it when missing.

        Args:
            frame_name:
                Frame name.

        Returns:
            Set[Tuple[str, str]]: Mutable spell-key set.
        """
        spell_keys = self.spell_keys_by_frame_name.get(frame_name)
        if spell_keys is None:
            spell_keys = set()
            self.spell_keys_by_frame_name[frame_name] = spell_keys
        return spell_keys

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
        spell_keys = self.spell_keys_by_conduit_id.get(conduit_id)
        if spell_keys is None:
            spell_keys = set()
            self.spell_keys_by_conduit_id[conduit_id] = spell_keys
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
        spell_keys = self.spell_keys_by_spellbook_id.get(spellbook_id)
        if spell_keys is None:
            spell_keys = set()
            self.spell_keys_by_spellbook_id[spellbook_id] = spell_keys
        return spell_keys

    def _discard_conduit_from_frame_index(
            self,
            frame_name: Optional[str],
            conduit_id: str,
    ) -> None:
        """
        Remove one conduit id from the frame grouping index.

        Args:
            frame_name:
                Frame name when known.
            conduit_id:
                Conduit id to discard.

        Returns:
            None.
        """
        if not frame_name:
            return
        conduit_ids = self.conduit_ids_by_frame_name.get(frame_name)
        if conduit_ids is None:
            return
        conduit_ids.discard(conduit_id)
        if len(conduit_ids) == 0:
            self.conduit_ids_by_frame_name.pop(frame_name, None)

    def _discard_spell_from_indexes(self, record: SpellRecord) -> None:
        """
        Remove one spell record's key from all secondary indexes.

        Args:
            record:
                Spell record whose key should be removed.

        Returns:
            None.
        """
        record_key = record.record_key
        frame_spell_keys = self.spell_keys_by_frame_name.get(record.frame_name)
        if frame_spell_keys is not None:
            frame_spell_keys.discard(record_key)
            if len(frame_spell_keys) == 0:
                self.spell_keys_by_frame_name.pop(record.frame_name, None)

        spellbook_spell_keys = self.spell_keys_by_spellbook_id.get(
            record.origin_spellbook_id
        )
        if spellbook_spell_keys is not None:
            spellbook_spell_keys.discard(record_key)
            if len(spellbook_spell_keys) == 0:
                self.spell_keys_by_spellbook_id.pop(
                    record.origin_spellbook_id,
                    None,
                )

        if record.owner_conduit_id:
            conduit_spell_keys = self.spell_keys_by_conduit_id.get(
                record.owner_conduit_id
            )
            if conduit_spell_keys is not None:
                conduit_spell_keys.discard(record_key)
                if len(conduit_spell_keys) == 0:
                    self.spell_keys_by_conduit_id.pop(
                        record.owner_conduit_id,
                        None,
                    )
