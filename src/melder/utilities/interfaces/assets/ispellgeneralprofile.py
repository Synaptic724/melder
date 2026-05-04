import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

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

    def to_descriptor_payload(self) -> "ISpellDescriptorPayload":
        """
        Export one descriptor-safe spell payload.

        Returns:
            ISpellDescriptorPayload: Descriptor-safe spell payload.
        """
        ...
