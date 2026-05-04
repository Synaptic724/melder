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
class INexusFrameManager(ICleanable, Protocol):
    """
    Interface for the Nexus-managed frame authoring facade.

    Purpose:
        Expose the authored-frame creation contract used by collaborators that
        should depend on the frame-manager capability surface without importing
        the concrete runtime implementation directly.

    Contract:
        - Realizes only Nexus-managed frames that satisfy the fixed
          dynamic/AI-native/Rift-enabled posture contract.
        - Consumes authored `NexusFrameConfiguration` objects as immutable
          inputs to frame realization.
        - Returns rooted `IConduit` objects for the realized Nexus-managed
          workspace.
    """

    def create(
            self,
            configuration: "NexusFrameConfiguration",
    ) -> "IConduit":
        """
        Realize one rooted Nexus-managed conduit from authored configuration.

        Returns:
            IConduit: Root conduit for the realized Nexus-managed workspace.
        """
        ...
