import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@runtime_checkable
class IRiftMemory(Protocol):
    """
    Interface for one immutable Rift execution memory record.
    """

    memory_id: str
    created_at: str
    frame_name: str
    action_name: str
    step_counter: int
    epoch_counter: int

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the memory metadata mapping.
        """
        ...
