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
class IFrameDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe frame payload contract.

    Purpose:
        Define the minimum descriptor-safe frame payload shape stored by
        `FrameRecord`.
    """

    system_state: Any
    ai_native_enabled: bool
    rift_enabled: bool
    root_conduit_count: int
    root_conduit_ids: Tuple[str, ...]
    named_root_conduits: Tuple[Tuple[str, str], ...]
    conduit_cloud_entry_count: int
    conduit_cloud_names: Tuple[str, ...]
    cluster_count: int
    cluster_names: Tuple[str, ...]
