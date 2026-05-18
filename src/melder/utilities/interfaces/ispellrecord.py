"""
Protocol contract for Nexus-published spell records.
"""

from typing import Any, Optional, Protocol, Tuple, runtime_checkable
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispelldescriptorpayload import ISpellDescriptorPayload


@runtime_checkable
class ISpellRecord(ICleanable, Protocol):
    """
    Descriptor-facing spell record contract.

    Purpose:
        Define the published, descriptor-safe spell metadata carried by
        `SpellRecord` and consumed by Nexus viewer, command, and ACL surfaces.

    Contract:
        - Represents one published `(origin_spellbook_id, spell_id)` pair.
        - Carries spell identity, frame provenance, access posture, and one
          descriptor-safe payload object.
        - Exposes descriptor-facing metadata only; it does not expose the live
          runtime `Spell` object or any mutating spellbook surface.
    """

    @property
    def nexus_label(self) -> str:
        """
        Return the published Nexus dataset label for this record.
        """
        ...

    @property
    def nexus_version(self) -> str:
        """
        Return the published Nexus dataset version for this record.
        """
        ...

    @property
    def origin_spellbook_id(self) -> str:
        """
        Return the owning Spellbook identifier that published this record.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name for this published spell record.
        """
        ...

    @property
    def owner_conduit_id(self) -> Optional[str]:
        """
        Return the owning conduit identifier when the spell has rooted runtime
        ownership.
        """
        ...

    @property
    def spell_id(self) -> str:
        """
        Return the current published spell/version identifier.
        """
        ...

    @property
    def spell_index_id(self) -> str:
        """
        Return the stable SpellIndex lineage identifier for this spell.
        """
        ...

    @property
    def spell_name(self) -> str:
        """
        Return the human-readable published spell name.
        """
        ...

    @property
    def spellframe(self) -> Any:
        """
        Return the published logical spellframe value exactly as carried by the
        runtime record.
        """
        ...

    @property
    def binding_name(self) -> Optional[str]:
        """
        Return the optional published binding name used to disambiguate spells
        under the same frame.
        """
        ...

    @property
    def permissions(self) -> Permissions:
        """
        Return the published permission posture for this spell record.
        """
        ...

    @property
    def existence(self) -> Existence:
        """
        Return the published existence policy for this spell record.
        """
        ...

    @property
    def payload(self) -> ISpellDescriptorPayload:
        """
        Return the descriptor-safe spell payload owned by this record.
        """
        ...

    @property
    def record_key(self) -> Tuple[str, str]:
        """
        Return the canonical spell-record key.

        Contract:
            - Keys the record by originating spellbook plus current spell id.
            - Uses the published spell/version id, not the stable lineage id.

        Returns:
            Tuple[str, str]: `(origin_spellbook_id, spell_id)`.
        """
        ...
