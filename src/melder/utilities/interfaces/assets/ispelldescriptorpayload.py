import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.idescriptorpayload import IDescriptorPayload

@runtime_checkable
class ISpellDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe spell payload contract.

    Purpose:
        Define the minimum sanitized spell payload shape stored by `SpellRecord`.
    """

    payload_type: str
    source_profile_name: Optional[str]
    source_profile_version: Optional[str]
    binding_payload: Dict[str, Any]
    resolution_payload: Any
    class_profile: Any
    callable_profile: Any
    metadata: Dict[str, Any]
    instance_members: Dict[str, Any]
    dynamic_access: Dict[str, bool]
