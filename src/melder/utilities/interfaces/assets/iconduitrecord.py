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
class IConduitRecord(ICleanable, Protocol):
    """
    Descriptor-facing conduit record contract.
    """

    nexus_label: str
    nexus_version: str
    conduit_id: str
    root_conduit_id: str
    frame_name: str
    origin_spellbook_id: Optional[str]
    payload: IConduitDescriptorPayload
