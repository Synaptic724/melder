from typing import Any, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
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
        - Mutable through explicit Nexus upsert/remove paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
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
        "binding_profile",
        "resolution_profile",
        "detailed_profile",
    ]

    def __init__(
            self,
            *,
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
            binding_profile: Any,
            resolution_profile: Any,
            detailed_profile: Any,
    ) -> None:
        """
        Initialize one canonical spell record.

        Args:
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
            binding_profile:
                Current binding profile payload.
            resolution_profile:
                Current resolution profile payload when available.
            detailed_profile:
                Current detailed profile payload when available.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
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
        self.binding_profile = binding_profile
        self.resolution_profile = resolution_profile
        self.detailed_profile = detailed_profile

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
        self.binding_profile = None
        self.resolution_profile = None
        self.detailed_profile = None
