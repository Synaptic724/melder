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
class IConduitDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe conduit payload contract.

    Purpose:
        Define the minimum descriptor-safe conduit payload shape stored by
        `ConduitRecord`.
    """

    conduit_name: Optional[str]
    conduit_state: Any
    policy: Any
    peer_conduit_ids: Tuple[str, ...]
    parent_conduit_id: Optional[str]
    lineage_depth: int
