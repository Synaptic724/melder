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
class IRiftEventSystem(ICleanable, Protocol):
    """
    Interface for the room-local Rift event system.
    """

    @property
    def rift_id(self) -> str:
        """
        Return the owning Rift id.
        """
        ...

    @property
    def space_id(self) -> str:
        """
        Return the owning space id.
        """
        ...

    @property
    def space_kind(self) -> str:
        """
        Return the owning space kind.
        """
        ...

    def register_event_callback(
            self,
            callback: Callable[[IRiftEvent], None],
    ) -> str:
        """
        Register one room-local event callback and return its subscription id.
        """
        ...

    def unregister_event_callback(self, subscription_id: str) -> None:
        """
        Remove one room-local event callback subscription by id.
        """
        ...

    def create_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> IRiftEvent:
        """
        Create one Rift-space runtime event without emitting it.
        """
        ...

    def emit_event(self, event: IRiftEvent) -> None:
        """
        Emit one Rift-space runtime event to all registered callbacks.
        """
        ...

    def create_and_emit_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> IRiftEvent:
        """
        Create one Rift-space runtime event and emit it immediately.
        """
        ...
