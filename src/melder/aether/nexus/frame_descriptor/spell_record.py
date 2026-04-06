from typing import Any, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.interfaces import ISpellDescriptorPayload
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class SpellRecord(Cleanable):
    """
    Internal

    Canonical Nexus record for one published spell.

    Purpose:
        Hold the spell-facing information the future frame/viewer model will
        consume without re-reading the owning Spellbook directly.

    Contract:
        - One record per `(origin_spellbook_id, spell_id)` key.
        - `owner_conduit_id` may be absent in theory, but the first passive
          ingest slice only publishes spells after conjure so it is normally
          populated.
        - Carries one deterministic Nexus publication contract.
        - Mutable through explicit Nexus upsert/remove paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "nexus_label",
        "nexus_version",
        "origin_spellbook_id",
        "frame_name",
        "owner_conduit_id",
        "spell_id",
        "lineage_id",
        "spell_name",
        "spellframe",
        "binding_name",
        "permissions",
        "existence",
        "payload",
    ]

    def __init__(
            self,
            *,
            nexus_label: str = "default",
            nexus_version: str = "0.0.1",
            origin_spellbook_id: str,
            frame_name: str,
            owner_conduit_id: Optional[str],
            spell_id: str,
            lineage_id: str,
            spell_name: str,
            spellframe: Any,
            binding_name: Optional[str],
            permissions: Permissions,
            existence: Existence,
            payload: ISpellDescriptorPayload,
    ) -> None:
        """
        Initialize one canonical spell record.

        Args:
            nexus_label:
                Published Nexus dataset label for this record.
            nexus_version:
                Published Nexus dataset version for this record.
            origin_spellbook_id:
                Owning Spellbook id.
            frame_name:
                Owning frame name.
            owner_conduit_id:
                Owning conduit id when known.
            spell_id:
                Current spell/version id.
            lineage_id:
                Stable SpellIndex lineage id.
            spell_name:
                Human-readable spell name.
            spellframe:
                Logical spellframe value as currently carried by the runtime.
            binding_name:
                Optional binding name.
            permissions:
                Spell permission posture.
            existence:
                Spell existence policy.
            payload:
                Sanitized spell descriptor payload for this record.
        """
        super().__init__()
        if not nexus_label:
            raise ValueError("nexus_label cannot be empty.")
        if not nexus_version:
            raise ValueError("nexus_version cannot be empty.")
        if payload is None:
            raise ValueError("payload cannot be None.")
        if not isinstance(payload, ISpellDescriptorPayload):
            raise TypeError("payload must satisfy ISpellDescriptorPayload.")
        self._id: str = IDBuilder.create_id()
        self.nexus_label = nexus_label
        self.nexus_version = nexus_version
        self.origin_spellbook_id = origin_spellbook_id
        self.frame_name = frame_name
        self.owner_conduit_id = owner_conduit_id
        self.spell_id = spell_id
        self.lineage_id = lineage_id
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.permissions = permissions
        self.existence = existence
        self.payload = payload

    @property
    def record_key(self) -> Tuple[str, str]:
        """
        Return the canonical Nexus storage key for this spell record.

        Returns:
            Tuple[str, str]: `(origin_spellbook_id, spell_id)`.
        """
        self.check_cleaned()
        return self.origin_spellbook_id, self.spell_id

    def cleanup(self) -> None:
        """
        Idempotently clear the record.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.nexus_label = None
        self.nexus_version = None
        self.origin_spellbook_id = None
        self.frame_name = None
        self.owner_conduit_id = None
        self.spell_id = None
        self.lineage_id = None
        self.spell_name = None
        self.spellframe = None
        self.binding_name = None
        self.permissions = None
        self.existence = None
        if self.payload is not None:
            self.payload.cleanup()
        self.payload = None
