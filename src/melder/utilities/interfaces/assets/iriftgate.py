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
class IRiftGate(ICleanable, Protocol):
    """
    Interface for the Rift-scoped gate primitive.
    """

    @property
    def enabled(self) -> bool:
        """
        Return whether admission is currently enabled.
        """
        ...

    @property
    def entry_mode(self) -> str:
        """
        Return the configured admission mode for this gate.
        """
        ...

    def open(self) -> None:
        """
        Enable admission and release waiting callers.
        """
        ...

    def close(self) -> None:
        """
        Disable admission so callers block in wait().
        """
        ...

    def wait(self) -> None:
        """
        Block until the gate is signalled open or terminally closed.
        """
        ...

    def admit(self) -> None:
        """
        Attempt to cross the gate using the configured admission mode.
        """
        ...

    def set_entry_mode(self, entry_mode: str) -> None:
        """
        Set the gate admission mode.
        """
        ...

    def register_ticket(self) -> None:
        """
        Register one in-flight operation.
        """
        ...

    def unregister_ticket(self) -> None:
        """
        Unregister one in-flight operation.
        """
        ...

    def has_active_tickets(self) -> bool:
        """
        Return whether at least one active ticket exists.
        """
        ...

    def active_ticket_count(self) -> int:
        """
        Return the current active ticket count.
        """
        ...

    def is_closed(self) -> bool:
        """
        Return whether the gate is terminally closed.
        """
        ...

    def close_and_wait_until_free(
            self,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close the gate and wait for ticket drain.
        """
        ...
