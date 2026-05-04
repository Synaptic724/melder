import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.iriftspace import IRiftSpace

@runtime_checkable
class ICodegenRiftSpace(IRiftSpace, Protocol):
    """
    Interface for CodegenRiftSpace.
    """

    @property
    def codegen_system(self) -> "ICodegenSystem":
        """
        Return the room-owned internal codegen system.
        """
        ...
