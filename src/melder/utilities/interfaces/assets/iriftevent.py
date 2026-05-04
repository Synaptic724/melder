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
class IRiftEvent(Protocol):
    """
    Interface for one emitted Rift-space runtime event.
    """

    event_id: str
    event_type: str
    emitted_at: str
    rift_id: str
    space_id: str
    space_kind: str
    frame_name: Optional[str]

    @property
    def payload(self) -> Dict[str, object]:
        """
        Return the event payload mapping.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the event metadata mapping.
        """
        ...
