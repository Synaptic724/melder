from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispell import ISpell
if TYPE_CHECKING:
    from melder.nexus.frame_descriptor.spell_descriptor_payload import SpellDescriptorPayload

@runtime_checkable
class ISpellGeneralProfile(ICleanable, Protocol):
    """
    Structural contract for the normal combined spell profile.

    Purpose:
        Represent the spell-owned profile that carries bind-time and
        resolution-time detail artifacts together.
    """

    profile_name: str
    profile_version: str
    binding_profile: Any
    resolution_profile: Any

    def complete_with_spell(self, spell: "ISpell") -> None:
        """
        Complete the profile using a fully formed spell.

        Args:
            spell: Fully formed spell instance.
        Returns:
            None.
        """
        ...

    def to_descriptor_payload(self) -> SpellDescriptorPayload:
        """
        Export one descriptor-safe spell payload.

        Returns:
            SpellDescriptorPayload: Descriptor-safe spell payload.
        """
        ...
